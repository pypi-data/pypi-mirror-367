import json
from pathlib import Path
from collections import defaultdict, deque

from django.core.management.base import BaseCommand
from django.db import connection, models
from django.apps import apps

MIGRATED_DATA_DIR = Path("migrated_data_chunks")


def load_all_chunks():
    records = []
    if MIGRATED_DATA_DIR.exists():
        for file in sorted(MIGRATED_DATA_DIR.glob("*.json")):
            with file.open("r", encoding="utf-8") as f:
                chunk_data = json.load(f)
                records.extend(chunk_data)
        return records
    else:
        return None


def build_dependency_graph(models):
    graph = defaultdict(set)
    for model in models:
        for field in model._meta.fields:
            if field.is_relation and field.related_model and field.related_model != model:
                if not field.remote_field or not field.remote_field.parent_link:
                    graph[model].add(field.related_model)
        if model not in graph:
            graph[model] = set()
    return graph


def topological_sort(graph):
    indegree = defaultdict(int)
    for node in graph:
        for dep in graph[node]:
            indegree[dep] += 1

    queue = deque([node for node in graph if indegree[node] == 0])
    sorted_models = []

    while queue:
        node = queue.popleft()
        sorted_models.append(node)
        for dep in graph[node]:
            indegree[dep] -= 1
            if indegree[dep] == 0:
                queue.append(dep)

    if len(sorted_models) != len(graph):
        raise Exception("Cycle detected in dependency graph!")

    return sorted_models


def truncate_table(model):
    with connection.cursor() as cursor:
        cursor.execute(f'TRUNCATE TABLE "{model._meta.db_table}" CASCADE;')


def reset_sequence(model):
    table_name = model._meta.db_table
    pk_field = model._meta.pk
    pk_name = pk_field.name

    if not isinstance(pk_field, (models.AutoField, models.BigAutoField, models.IntegerField)):
        print(f"⏭️ Skipping sequence reset for {model} because PK is not integer-based.")
        return

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', '{pk_name}'),
                COALESCE(MAX({pk_name}) + 1, 1),
                false
            ) FROM {table_name}
        """)


def sort_self_fk_records(records, fk_field_name, pk_name):
    by_pk = {}
    children_map = defaultdict(list)
    roots = []

    for record in records:
        pk = record.get(pk_name)
        parent_id = record.get(fk_field_name)
        by_pk[pk] = record
        if parent_id:
            children_map[parent_id].append(pk)
        else:
            roots.append(pk)

    sorted_pks = []
    visited = set()

    def visit(pk):
        if pk in visited:
            return
        visited.add(pk)
        for child_pk in children_map.get(pk, []):
            visit(child_pk)
        sorted_pks.append(pk)

    for root_pk in roots:
        visit(root_pk)

    return [by_pk[pk] for pk in reversed(sorted_pks)]


def update_or_create_records(model, records):
    pk_name = model._meta.pk.name

    self_fk_fields = [
        field.name for field in model._meta.fields
        if field.is_relation and field.related_model == model and not field.remote_field.parent_link
    ]

    if self_fk_fields:
        for fk_field in self_fk_fields:
            records = sort_self_fk_records(records, fk_field, pk_name)

    print(f"step1 {model} --> {self_fk_fields}")

    for record in records:
        data = record.copy()
        obj_pk = data.pop(pk_name, None)
        parent_fks = {fk: data.pop(f"{fk}_id", None) for fk in self_fk_fields}

        if obj_pk is None:
            print(f"⚠️ Skipping record without PK ({pk_name}): {record}")
            continue

        try:
            obj, created = model.objects.get_or_create(**{pk_name: obj_pk}, defaults=data)
        except Exception as e:
            print(f"⚠️ Exception on get_or_create for record ({pk_name}): {record}")
            print(f"Exception: {e}")
            continue

        if not created:
            for fk_field in self_fk_fields:
                setattr(obj, fk_field, None)
            for k, v in data.items():
                setattr(obj, k, v)
            obj.save()

        record["_created_obj"] = obj
        record["_parent_fks"] = parent_fks

    print(f'start step 2 {model}')

    for record in records:
        if "_created_obj" not in record:
            continue
        obj = record["_created_obj"]
        parent_fks = record["_parent_fks"]

        updated_fields = []
        for fk_field, parent_pk in parent_fks.items():
            if parent_pk:
                setattr(obj, fk_field, model.objects.get(pk=parent_pk))
                updated_fields.append(fk_field)

        if updated_fields:
            obj.save(update_fields=updated_fields)


class Command(BaseCommand):
    help = "Load and update records from chunked JSON files with dependency handling"

    def add_arguments(self, parser):
        parser.add_argument('--exclude-apps', nargs='+', help='Exclude these apps from loading')
        parser.add_argument('--exclude-tables', nargs='+', help='Exclude specific models (app_label.ModelName)')
        parser.add_argument('--load-apps', nargs='+', help='Only include these apps')
        parser.add_argument('--load-tables', nargs='+', help='Only include specific models (app_label.ModelName)')

    def handle(self, *args, **options):
        all_records = load_all_chunks()

        if not all_records:
            self.stdout.write(self.style.ERROR(f"No chunk files found in {MIGRATED_DATA_DIR}"))
            return

        exclude_apps = set(options.get("exclude_apps") or [])
        exclude_tables = set(options.get("exclude_tables") or [])
        load_apps = set(options.get("load_apps") or [])
        load_tables = set(options.get("load_tables") or [])

        grouped = {}
        for item in all_records:
            app_label = item["app"]
            model_name = item["model"]
            truncate = item["truncate"]
            record = item["record"]

            full_label = f"{app_label}.{model_name}"

            if load_apps and app_label not in load_apps:
                continue
            if load_tables and full_label not in load_tables:
                continue
            if exclude_apps and app_label in exclude_apps:
                continue
            if exclude_tables and full_label in exclude_tables:
                continue

            key = (app_label, model_name)
            if key not in grouped:
                grouped[key] = {"truncate": truncate, "records": []}
            grouped[key]["records"].append(record)

        model_map = {}
        for (app_label, model_name) in grouped:
            try:
                model = apps.get_model(app_label, model_name)
                model_map[model] = grouped[(app_label, model_name)]
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"Error loading model {app_label}.{model_name}: {e}"))

        dep_graph = build_dependency_graph(model_map.keys())
        sorted_models = topological_sort(dep_graph)

        self.stdout.write(self.style.NOTICE(f"Dependency Graph:"))
        for model, deps in dep_graph.items():
            self.stdout.write(self.style.NOTICE(f"  {model._meta.label} depends on {[d._meta.label for d in deps]}"))

        self.stdout.write(self.style.NOTICE(f"Processing order:"))
        for m in sorted_models:
            self.stdout.write(self.style.NOTICE(f"  {m._meta.label}"))

        try:
            for model in reversed(sorted_models):
                data = model_map.get(model)
                if not data:
                    continue
                truncate = data["truncate"]
                records = data["records"]

                self.stdout.write(self.style.NOTICE(
                    f"Processing {model._meta.label} ({len(records)} records)"
                ))

                if truncate or True:
                    self.stdout.write(self.style.NOTICE(
                        f"Truncating {model._meta.db_table}"
                    ))
                    truncate_table(model)

                update_or_create_records(model, records)
                reset_sequence(model)

                self.stdout.write(self.style.SUCCESS(
                    f"✅ Done: {model._meta.label}"
                ))

        finally:
            ...

        self.stdout.write(self.style.SUCCESS(
            f"🎉 All chunks loaded successfully!"
        ))
