import json
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
import sys
from ...utils import get_all_subclasses

from django.core.management.base import BaseCommand


MIGRATED_DATA_DIR = Path("migrated_data_chunks")
MAX_RECORDS_PER_FILE = 5000


def default_serializer(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return float(o)
    return str(o)


class Command(BaseCommand):
    help = "Generate chunked feature files with initial data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all_tables",
            action="store_true",
            help="Export all tables regardless of 'migratable_data'"
        )
        parser.add_argument(
            "--exclude",
            nargs="*",
            default=[],
            help="List of app_label.model_name to exclude when using --all_tables"
        )

    def handle(self, *args, **options):
        from django.db.models import Model, ForeignKey, ManyToManyField

        all_tables = options["all_tables"]
        exclude = set(item.lower() for item in options["exclude"])
        print(exclude)

        all_subclasses = get_all_subclasses(Model)
        print(f"Found subclasses: {[cls.__name__ for cls in all_subclasses]}")

        MIGRATED_DATA_DIR.mkdir(exist_ok=True)

        for old_file in MIGRATED_DATA_DIR.glob("*.json"):
            old_file.unlink()
            print(f"Deleted old chunk file: {old_file.name}")

        flat_records = []

        for cls in all_subclasses:
            meta = getattr(cls, "_meta", None)
            app_label = meta.app_label
            model_name = meta.model_name
            full_name = f"{app_label}.{model_name}".lower()

            if not all_tables and not getattr(cls, 'migratable_data', False):
                continue
            if all_tables and full_name in exclude:
                print(f"⛔ Excluded model: {full_name}")
                continue

            truncate = True if all_tables else getattr(cls, "truncate_on_migrate_data", False)

            print(full_name)
            records = list(cls.objects.all().values())
            print(f"Processing: {full_name}  -->  Records: {len(records)}")

            ##
            map_fields = dict()
            for field in meta.fields:
                # if isinstance(field, (ForeignKey, ManyToManyField)):
                #     print(f"{field.name}--> {field.__dict__}")
                if isinstance(field, (ForeignKey, )) and (getattr(field, "to_fields", None) not in [["id"], [None]]
                        or getattr(field, "old_to_field", None) is not None):
                    ##todo for manytomany
                    map_fields[f"{field.name}_id"] = {"model": field.related_model, "from": getattr(field, "old_to_field", "id"),
                                              "to": getattr(field, "to_fields", ["id"])[0]}

            if map_fields:
                print(f"map_fields: {map_fields}")

            ##

            for _record in records:
                for field in map_fields:
                    try:
                        obj = map_fields[field]["model"].objects.filter(**{map_fields[field]["from"]: _record[field]})
                        if obj.count() > 0:
                            _record[field] = getattr(obj.first(), map_fields[field]["to"])
                    except Exception as e:
                        ...
                flat_records.append({
                    "app": app_label,
                    "model": model_name,
                    "truncate": truncate,
                    "record": _record
                })

        print(f"Total records collected: {len(flat_records)}")

        def chunk_list(lst, size):
            for i in range(0, len(lst), size):
                yield lst[i:i + size]

        for idx, chunk in enumerate(chunk_list(flat_records, MAX_RECORDS_PER_FILE), start=1):
            file_path = MIGRATED_DATA_DIR / f"migrated_data_part{idx}.json"
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(chunk, f, indent=4, ensure_ascii=False, default=default_serializer)
            print(f"Written {len(chunk)} records to {file_path}")

        self.stdout.write(self.style.SUCCESS(
            f"✅ Chunked feature data saved in '{MIGRATED_DATA_DIR}/'"
        ))
