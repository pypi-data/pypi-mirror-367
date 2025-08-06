import re
from django.db import models
from rest_framework.exceptions import PermissionDenied
from .local_user import get_current_user
from django.db.models.expressions import RawSQL
from django.db.models.sql import Query
from django.db.models.sql.datastructures import BaseTable

from .utils import safe_convert


class CustomQuerySet(models.QuerySet):
    def filter_active(self, is_active=True):
        return self.filter(is_active=is_active)

    def filter_by_publish(self):
        if any(f.name == 'publish' for f in self.model._meta.get_fields()):
            return self.filter(publish=True)
        return self

    def filter_by_active_user(self, user):
        # if self.model.user_has_permission():
        #     return self.all()
        return self.filter(user=user)


class CustomRelatedNameManager:
    def __init__(self, related_name, filter_kwargs=None, orders=None, function=None, qs_item_count=None, **kwargs):
        self.related_name = related_name
        self.filter_kwargs = filter_kwargs or {}
        self.orders = orders or []
        self.function = function
        self.field = None
        self.manager = None
        self.qs_item_count = qs_item_count

    def resolve_related_metadata(self, instance):
        if self.field is not None:
            return
        related_name = getattr(instance, self.related_name)  # or getattr(instance.__class__, self.related_name, None)
        if related_name:
            self.field = related_name.field
            self.manager = related_name

    def __get__(self, instance, instance_type=None):
        if instance is None :
            return self
        self.resolve_related_metadata(instance)
        if not self.manager or not instance.pk:
            return self
        related_name = getattr(instance, self.related_name)
        # related_name = self.manager
        filters = {
            key: (getattr(instance, value.split('.')[1], None) if len(value.split('.')) > 1 else instance) if str(
                value).__contains__('self') else value for key, value in self.filter_kwargs.items() if
            not (isinstance(value, list) and len(value) == 2 and not eval(value[0].replace("self", "instance")))}
        if self.function:
            related_name = self.function(related_name, obj=self, instance=instance)
        queryset = related_name.filter(**filters).order_by(*self.orders) if self.orders else related_name.filter(
            **filters)
        if self.qs_item_count:
            limited_queryset = queryset[:self.qs_item_count]
            queryset = queryset.filter(pk__in=[item.pk for item in limited_queryset])
        return queryset


class CustomGenericRelation:
    def __init__(self, generic_model, to_field, filter_kwargs=None, orders=None, function=None, qs_item_count=None, **kwargs):
        self.filter_kwargs = filter_kwargs or {}
        self.orders = orders or []
        self.function = function
        field_name = to_field.split("__")[0]
        self.field = generic_model._meta.get_field(field_name)
        self._to_field = to_field
        if len(to_field.split("__")) > 1:
            _ = to_field.split("__")[-1]
            self.to_fields = [None if _ in [None, 'pk'] else _]
        else:
            self.to_fields = to_field
        self.manager = generic_model.objects
        self.is_generic_relation = True
        self.qs_item_count = qs_item_count
        self.generic_model = generic_model

    def resolve_related_metadata(self, instance):
        setattr(self.field, 'to_fields', self.to_fields)
        # if self.field is not None:
        #     return
        # self.field = related_name.field
        # self.manager = related_name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        self.resolve_related_metadata(instance)
        if not self.manager or instance.pk is None:
            return self
        related_name = self.manager
        filters = {
            key: (getattr(instance, value.split('.')[1], None) if len(value.split('.')) > 1 else instance) if str(
                value).__contains__('self') else value for key, value in self.filter_kwargs.items() if
            not (isinstance(value, list) and len(value) == 2 and not eval(value[0].replace("self", "instance")))}
        if self.function:
            related_name = self.function(related_name, obj=self, instance=instance)
        if instance.pk is not None:
            filters.update({self._to_field: instance.pk})
        queryset = related_name.filter(**filters).order_by(*self.orders) if self.orders else related_name.filter(
            **filters)
        if self.qs_item_count:
            limited_queryset = queryset[:self.qs_item_count]
            queryset = queryset.filter(pk__in=[item.pk for item in limited_queryset])

        queryset.filters = filters
        return queryset


class CustomBaseTable(BaseTable):
    def __init__(self, table_name, alias):
        super().__init__('custom_table', alias)

    def as_sql(self, compiler, connection):
        base, params = super().as_sql(compiler, connection)
        return f"({compiler.row_query}) custom_table", params


class CustomQuery(Query):
    row_query = None
    base_table_class = CustomBaseTable

    def __init__(self, model, row_query=None, with_sql_commands=''):
        super().__init__(model)
        self.row_query = row_query
        self.with_sql_commands = with_sql_commands

    def __compiler_as_sql(self, with_limits=True, with_col_aliases=False):
        final_sql, params = self.as_sql0(with_limits=with_limits, with_col_aliases=with_col_aliases)

        if final_sql.startswith("SELECT"):
            final_sql = f'''--with_start
{self.with_sql_commands}
--with_end 
{final_sql}'''

        matches = list(re.finditer(r"--with_start(.*?)--with_end", final_sql, re.DOTALL))
        if matches:
            first_match_end = matches[0].end()
            final_sql = final_sql[:first_match_end] + re.sub(r"--with_start(.*?)--with_end", "",
                                                             final_sql[first_match_end:],
                                                             flags=re.DOTALL)

        return final_sql, params

    def get_compiler(self, using=None, connection=None, elide_empty=True):
        compiler = super().get_compiler(using, connection, elide_empty)
        compiler.row_query = self.row_query
        self.as_sql0 = compiler.as_sql
        compiler.as_sql = self.__compiler_as_sql
        # self.compiler_ = compiler

        return compiler


class CustomManager(models.Manager):
    def __init__(self):
        super().__init__()
        self._db = "default"
        self.queryset = None
        self._queryset_class = CustomQuerySet
        self._queryset_class.get_query_fields = self.get_query_fields

    def custom_raw(self, raw_query, with_sql_commands='', select_list=None, **params):
        if not select_list:
            select_list = []
        if isinstance(raw_query, str):
            raw_query = CustomQuery(self.model, raw_query, with_sql_commands)
            res = super().get_queryset()
            res.query = raw_query
        else:
            res = raw_query(**params)

        for select in select_list:
            if isinstance(select, (list, tuple)):
                res = res.annotate(**{select[0]: RawSQL(select[1], [])})
                # res = res.extra(select=select)
                # setattr(self.model, select.keys()[0], None)
            else:
                res = res.annotate(**{select: RawSQL(select, [])})
                # res = res.extra({f"{select}": select})
                # setattr(self.model, select, None)
        return res

    def get_queryset(self):
        if getattr(self.model, 'fiscal_delete', True):
            return self._queryset_class(model=self.model, using=self._db, hints=self._hints)
        else:
            return self._queryset_class(model=self.model, using=self._db, hints=self._hints).filter(is_deleted=False)

    @staticmethod
    def get_query_fields(obj):
        if not getattr(obj, 'query_fields', None):
            obj.query_fields = [field.name for field in obj.model._meta.get_fields()] + list(
                obj.query.annotations.keys())
        return obj.query_fields

    def get_queryset_active_filter(self, is_active=True):
        return self.get_queryset().filter_active(is_active=is_active)


class CustomActiveUserManager(CustomManager):
    allowed_group_name = 'admin'
    def get_queryset(self, filter_by_active_user=True):
        qs = super().get_queryset()
        user = get_current_user()
        if not user or not user.is_authenticated:
            return qs.none()
        if filter_by_active_user and not user.is_superuser:

            qs = qs.filter_by_active_user(user)
        return qs

    @classmethod
    def check_access_user(cls, user):
        if user.is_superuser:
            return True
        return user.groups.filter(name=cls.allowed_group_name).exists()