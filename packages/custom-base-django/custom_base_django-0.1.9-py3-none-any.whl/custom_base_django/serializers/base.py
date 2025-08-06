import decimal
from datetime import date, datetime
from decimal import Decimal
from django.db import models
from django.db.models import QuerySet, Q
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (  # NOQA # isort:skip
    BooleanField, CharField, ChoiceField, DateField, DateTimeField, DecimalField,
    DictField, DurationField, EmailField, Field, FileField, FilePathField, FloatField,
    HiddenField, HStoreField, IPAddressField, ImageField, IntegerField, JSONField,
    ListField, ModelField, MultipleChoiceField, ReadOnlyField,
    RegexField, SerializerMethodField, SlugField, TimeField, URLField, UUIDField,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import as_serializer_error, raise_errors_on_nested_writes
from django.contrib.postgres.fields import ArrayField
# from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.utils import model_meta
from django.apps import apps

from ..utils import model_fields_type_map, FreeField, first_upper, get_limits
from ..models.custom_fields import RelatedListField, SmartFileListField,CaseInsensitiveUniqueCharField
from .custom_fields import RelatedListSerializerField, SmartFileListSerializerField, CustomDecimalField
from ..signals import *


class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'  # برای تنظیم تعداد آیتم‌ها در هر صفحه از طریق پارامتر URL
    max_page_size = 200

    def get_paginated_response(self, data):
        return {
            'count': self.page.paginator.count,  # تعداد کل آیتم‌ها
            'total_pages': self.page.paginator.num_pages,  # تعداد کل صفحات
            'current_page': self.page.number,  # شماره صفحه فعلی
            'next': self.get_next_link(),  # لینک صفحه بعدی
            'previous': self.get_previous_link(),  # لینک صفحه قبلی
            'results': data  # داده‌های صفحه فعلی
        }


serializer_list = dict()

__all__ = ['DynamicFieldsModelSerializer', 'NesteSerializerDefinition', ]


MAP = {
    "integer": 0,
    "float": 0.0,
    "char": "",
    "datetime": "2024-01-01",
    "boolean": False,
}


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = {
        # مپ کردن کاستوم فیلد
        SmartFileListField: SmartFileListSerializerField,
        RelatedListField: RelatedListSerializerField,
        ArrayField: ListField,
        models.DecimalField: CustomDecimalField,
        CaseInsensitiveUniqueCharField: CharField,
        # دیفالت خود سریالایزر
        models.JSONField: JSONField,
        models.AutoField: IntegerField,
        models.BigIntegerField: IntegerField,
        models.BooleanField: BooleanField,
        models.CharField: CharField,
        models.CommaSeparatedIntegerField: CharField,
        models.DateField: DateField,
        models.DateTimeField: DateTimeField,
        models.DurationField: DurationField,
        models.EmailField: EmailField,
        models.Field: ModelField,
        models.FileField: FileField,
        models.FloatField: FloatField,
        models.ImageField: ImageField,
        models.IntegerField: IntegerField,
        models.NullBooleanField: BooleanField,
        models.PositiveIntegerField: IntegerField,
        models.PositiveSmallIntegerField: IntegerField,
        models.SlugField: SlugField,
        models.SmallIntegerField: IntegerField,
        models.TextField: CharField,
        models.TimeField: TimeField,
        models.URLField: URLField,
        models.UUIDField: UUIDField,
        models.GenericIPAddressField: IPAddressField,
        models.FilePathField: FilePathField,
    }

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(field_name, model_field)
        function = getattr(model_field, 'extra_field_kwargs', None)
        if function:
            field_kwargs = function(model_field, field_kwargs)
        # if isinstance(model_field, SmartFileListField):
        #     field_class.upload_subfolder = model_field.upload_subfolder
        #     field_class.prefix_file_name = model_field.prefix_file_name
        # elif isinstance(model_field, RelatedListField):
        #     field_class._related_model_raw = model_field._related_model_raw
        #     field_class.to_field = model_field.to_field
        #     field_class.struct_name = model_field.struct_name
        return field_class, field_kwargs

    class BaseStruct:
        def __init__(self):
            self.nested = dict()
            self.nested_fields = dict()
            self.extra_non_required_fields = list()
            self.extra_writable_fields = list()
            self.readonly_fields = list()
            self.exclude_fields = list()
            self.extra_fields = list()
            self.extra_validations = list()
            self.blank_objects = dict()
            self.pk_field = None
            self.model = None
            self.must_save = True
            self.need_authentication = True
            self.custom_query = dict()
            # self.redirect_url = None

            self.fields = None
            self.model = None
            self.ignore_readonly_fields = False
            self.with_nested = True
            self.include_metadata = True
            self.include_fks_str = True

        def get_serializer_base_class(self, struct_name):
            base_struct = self.__class__()
            if self.model:
                model_name = f"{self.model._meta.app_label}.{self.model._meta.model_name}"
                from ..models import BaseStructure
                obj = BaseStructure.objects.filter(struct_name=struct_name, model=model_name).first()
                if obj:
                    base_struct.extra_non_required_fields = obj.extra_non_required_fields if obj.extra_non_required_fields else self.extra_non_required_fields
                    base_struct.nested = obj.nested if obj.nested else self.nested
                    base_struct.nested_fields = obj.nested_fields if obj.nested_fields else self.nested_fields
                    base_struct.extra_writable_fields = obj.extra_writable_fields if obj.extra_writable_fields else self.extra_writable_fields
                    base_struct.readonly_fields = obj.readonly_fields if obj.readonly_fields else self.readonly_fields
                    base_struct.exclude_fields = obj.exclude_fields if obj.exclude_fields else self.exclude_fields
                    base_struct.extra_fields = obj.extra_fields if obj.extra_fields else self.extra_fields
                    base_struct.extra_validations = obj.extra_validations if obj.extra_validations else self.extra_validations
                    base_struct.blank_objects = obj.blank_objects if obj.blank_objects else self.blank_objects
                    base_struct.pk_field = obj.pk_field if obj.pk_field else self.pk_field
                    base_struct.model = obj.model if obj.model else self.model
                    base_struct.must_save = obj.must_save if obj.must_save else self.must_save
                    base_struct.need_authentication = obj.need_authentication if obj.need_authentication else self.need_authentication
                    base_struct.custom_query = obj.custom_query if obj.custom_query else self.custom_query
                    base_struct.fields = obj.fields if obj.fields else self.fields
            return base_struct

        def to_dict(self):
            class_attrs = {attr: getattr(self.__class__, attr) for attr in dir(self.__class__) if
                           not attr.startswith("__")}
            instance_attrs = self.__dict__
            attrs = {attr: getattr(self, attr) for attr in {**class_attrs, **instance_attrs} if
                     attr not in ['to_dict', 'nested', 'fields']}
            return {**self.nested, **attrs}

        def __get__(self, obj, obj_type=None):
            self.model = obj_type
            return self

    pagination_class = CustomPagination
    nested_fields = dict()
    extra_non_required_fields = list()
    extra_writable_fields = list()
    extra_fields = list()
    readonly_fields = list()
    exclude_fields = list()
    blank_objects = dict()
    pk_field = None
    model = None
    must_save = True
    need_authentication = True
    custom_query = dict()

    @property
    def data(self, **kwargs):
        super_data = super().data
        request_method = self.request_data.method if self.request_data else kwargs.get('request_data', None)
        if request_method == 'POST':
            past_post_res = self.past_post(instance=self.instance, data=super_data, **kwargs)
            if past_post_res:
                past_post_res = past_post_res.get('data')
                super_data['past_post_res'] = past_post_res
                past_post_error = past_post_res.get('errors')
                if past_post_error:
                    self.raise_validation_error(past_post_error['sub_type'], past_post_error['title'])
                # else:
                #     redirect_url = past_post_res.get('redirect_page')
                #     if redirect_url:
                #         url = redirect_url.get('url')
                #         return redirect(url)
            else:
                super_data['past_post_res'  ] = {}

            # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            #     self.form_struct_instance.funcs_res.get(
            #         form_name_, {}
            #     ).get('past_post_method_res', {})['redirect_page'] = full_url
            # self.context['form_structure'][]
            # return JsonResponse({'redirect_url': full_url})
        return super_data

    def pre_get(self, *args, **kwargs):
        ...

    def past_get(self, *args, **kwargs):
        ...

    def pre_post(self, *args, **kwargs):
        ...

    def past_post(self, *args, **kwargs):
        ...

    def pre_validation(self, *args, **kwargs):
        ...

    def past_validation(self, *args, **kwargs):
        ...

    extra_validations = list()

    @staticmethod
    def raise_validation_error(title="error", text="Some errors occurred!", code=1):
        raise ValidationError({title: text}, code=code)

    @classmethod
    def get_queryset(cls, view_obj, *args, **kwargs):
        queryset = cls.model.search_q(getattr(view_obj, 'search_q', ''), cls.custom_query, view_obj=view_obj)
        query_fields = queryset.get_query_fields() if hasattr(queryset, 'get_query_fields') else []
        func_filter = getattr(view_obj, 'get_dynamic_filters', None)
        queryset = queryset.filter(func_filter(query_fields)) if func_filter else queryset
        queryset = queryset.order_by(view_obj.order_by) if not queryset.ordered else queryset
        return queryset

    @classmethod
    def get_json_response(cls, view_obj, *args, **kwargs):
        if view_obj.instance:
            serializer = cls(view_obj.instance, include_metadata=view_obj.include_metadata, view_obj=view_obj)
            data = serializer.data
        else:
            queryset = cls.get_queryset(view_obj, *args, **kwargs)
            paginator = cls.pagination_class()
            result_page = paginator.paginate_queryset(queryset, view_obj.request)
            serializer = cls(result_page, with_nested=view_obj.with_nested, include_metadata=False, include_fks_str=True, many=True,
                             view_obj=view_obj)
            data = paginator.get_paginated_response(serializer.data)
            data.update({"meta_datas": cls(cls.model()).data.get("meta_datas")})
        return data, status.HTTP_200_OK  # JsonResponse(data, status=status.HTTP_200_OK,safe=False)

    @classmethod
    def post_json_data(cls, view_obj, *args, **kwargs):
        if view_obj.instance:
            serializer = cls(view_obj.instance, data=view_obj.request.data,
                             include_metadata=view_obj.include_metadata, view_obj=view_obj)
        else:
            serializer = cls(data=view_obj.request.data, view_obj=view_obj)
        serializer.must_save = view_obj.must_save
        if serializer.is_valid():
            created = not (view_obj.instance and view_obj.instance.pk)
            serializer.save()
            return serializer.data, status.HTTP_201_CREATED if created else status.HTTP_200_OK  # JsonResponse(serializer.data, status=status.HTTP_201_CREATED, safe=True)
        else:
            return serializer._errors, status.HTTP_400_BAD_REQUEST  # JsonResponse(serializer._errors, status=status.HTTP_400_BAD_REQUEST, safe=True)

    def __init_class__(self):
        if self.Meta.fields == '__all__':
            self.Meta.fields = [field for field in self.get_fields()]

        for field in self.fields:
            if isinstance(self.fields[field], serializers.ListSerializer):
                prop = getattr(self.model(), field)
                if prop is not None:
                    serializer_class = self.fields[field].child.__class__
                    if isinstance(prop, QuerySet):
                        self.__class__.nested_fields[field] = (None, None)
                        # self.__class__.blank_objects[f'blank_{field}'] = serializer_class(serializer_class.model())
                    elif hasattr(prop, 'field'):
                        self.__class__.nested_fields[field] = (
                        prop.field.name, prop.field.to_fields[0])  # cache_name replace with name
                        # self.__class__.blank_objects[f'blank_{field}'] = serializer_class(serializer_class.model())

        # self.Meta.fields = self.Meta.fields + self.model.related_properties + self.model.related_meta_properties + ['navigation_instances']

        self.__class__.writable_fields = set(self.Meta.fields)

    def pop_some_fields(self):
        if not self.with_nested:  # or (not getattr(self.instance, 'pk', None) and self.method == 'get'):
            for field in self.nested_fields.keys():
                self.fields.pop(field, None)

        # if not self.include_metadata:
        #     fields = [field for field in self.fields]
        #     for field in fields:
        #         if field.__contains__("_meta_data"):
        #             self.fields.pop(field, None)
        #     self.fields.pop('navigation_instances', None)

        # if not self.include_fks_str:
        #     for field in self.model.related_properties:
        #         self.fields.pop(field, None)

    # def __get__(self, instance, owner):
    #     self.parent_instance = instance
    #     self.parent_class = owner
    #     if instance:
    #         self.user = instance.user
    #         self.set_limits(instance.limits_list, nested_key=self.nested_key)
    #     return self

    def set_limits(self, limits_list=None, nested_key='', user=None, instance=None):
        instance = instance or self.instance
        # if instance is None:
        #     return
        limits_list = limits_list or self.limits_list or []
        nested_key = nested_key or self.nested_key or ''
        user = user or self.user or self.model.request_user or ''
        base_limits = self.model.get_limits(user)
        base_limits = get_limits(limits_list, user=user, nested_key=nested_key, base_limits=base_limits)

        for f_name in base_limits.get('drop', []):
            self.fields.pop(f_name, None)

        for f_name in base_limits.get('readonly', []):
            field = self.fields.get(f_name)
            field.read_only = True


        for f_name in base_limits.get('required', []):
            field = self.fields.get(f_name)
            field.required = True
            field.allow_null = False

        for f_name in base_limits.get('hidden', []):
            field = self.fields.get(f_name)
            field.hidden = True

        self.readonly_fields.extend(base_limits.get('readonly', []))
        self.base_limits = base_limits

    def __init__(self, *args, with_nested=None, ignore_readonly_fields=None, include_metadata=None,
                 include_fks_str=None, parent_field=None, view_obj=None,
                 nested_key='', limits_list=None, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.nested_fields.keys():
            self.fields[field].child.parent_obj = self

        self.with_nested = self.with_nested if with_nested is None else with_nested
        self.include_metadata = self.include_metadata if include_metadata is None else include_metadata
        self.include_fks_str = self.include_fks_str if include_fks_str is None else include_fks_str
        # limits_list = [{"groups":[], "users":[1],
        #                 "readonly":[], "drop":["status"], "hidden":[], "required":[],
        #                 "nesteds":{"variant_products":{"readonly":[], "drop":["id"], "hidden":["images"], "required":[]}}},
        #                ]
        self.limits_list = limits_list or getattr(self, 'limits_list', None) or []
        self.nested_key = nested_key or ''
        self.view_obj = view_obj
        ignore_readonly_fields = view_obj.ignore_readonly_fields if view_obj else ignore_readonly_fields
        self.ignore_readonly_fields = ignore_readonly_fields or self.ignore_readonly_fields
        self.request_data = self.view_obj.request if self.view_obj else kwargs.get('request_data', None)
        self.base_limits = {}
        self.user = view_obj.request.user if view_obj else None
        self.nested_datas = dict()
        self.nested_instances = dict()
        self.pop_some_fields()
        # self.set_limits()
        pk_field = self.fields.get(self.pk_field)
        if pk_field:
            self.fields.get(self.pk_field).required = False

        # self.include_metadata = kwargs.pop('metadata', True)
        for field in self.exclude_fields:
            self.fields.pop(field, None)

        if parent_field:
            f = self.fields.get(parent_field)
            if f:
                f.read_only = True

        for field in self.extra_non_required_fields:
            f = self.fields.get(field)
            if f:
                f.required = False
                f.allow_blank = True
                f.allow_null = True

        for field in self.readonly_fields:
            f = self.fields.get(field)
            if f:
                f.read_only = True

        # for field in self.fields:
        #     if self.fields[field].read_only and self.model.has_setter(field):
        #         self.fields[field] = FreeField(required=False, read_only=False, allow_blank=True, allow_null=True)

        # if kwargs.get('data'):
        #     self.__nested_init__(**kwargs)

    def get_structure(self, required_only=False, required_status=False):
        fields = dict()
        for field in self.fields:
            if field in self.nested_fields:
                type_str = self.fields[field].child.get_structure(required_only, required_status)
            else:
                type_str = str(type(self.fields[field])).replace("<class 'rest_framework.fields.", "").replace(
                    "Field'>", "")
                type_str = type_str.replace("<class 'rest_framework.relations.PrimaryKeyRelated", "f_key")
                type_str = type_str.replace("<class 'rest_framework.serializers.ListSerializer'>", "dict")
                type_str = type_str.lower()
                type_str = type_str.replace("<class 'sepidar_api.serializers.customdecimal", "float")
                type_str = MAP.get(type_str, type_str)
                if type_str == "f_key":
                    type_str = str(self.fields[field].queryset.model).lower()
                    type_str = type_str.split(".")[-1].replace("'>", "")
                    type_str = f"rel({type_str})"
            if required_only:
                if self.fields[field].required or field in self.nested_fields:
                    fields[field] = type_str
            else:
                if required_status and self.fields[field].required:
                    fields[field] = f"{type_str} (*)"
                else:
                    fields[field] = type_str

        return fields

    # تبدیل اطلاعات دیتا به اطلاعات معتبر منطبق بر فیلد های مدل. همچنین برخی پراپرتی ها که ستر دارند و در دیتا امده اند هم در دیتای ولید شده اضافه می شوند
    # def to_internal_value(self, data):
    #     try:
    #         value = super().to_internal_value(data)
    #         return value
    #     except Exception as e:
    #         raise e

    # بازنویسی به صورتی که نستد را ساپورت میکند و ابجکت جاری را برای نستد ها ست میکند. همچنین حالت سیو فالس را هم
    # ساپورت میکند
    def save(self, **kwargs):
        errors = {}
        # self.instance = super().save(**kwargs)
        pre_post_res = self.pre_post(instance=self.instance, **kwargs)
        errors['pre_post_error'] = pre_post_res.get('data', {}).get('errors') if pre_post_res else None

        if self.must_save and not errors['pre_post_error']:
            serializer_pre_save.send(sender=self.model, serializer=self, instance=self.instance, **kwargs)
            self.instance.save(**kwargs)
            # دخیره سازی اطلاعات مثل عکس کاستوم شده و ... که نیاز به گرفتن ایدی عکس دارند
            _post_actions = getattr(self, "_post_actions", [])
            updated_fields = []
            if _post_actions:
                for item in _post_actions:
                    item["action"](self.instance)
                    updated_fields.append(item["field_name"])
                self.instance.save(updated_fields=updated_fields)
            for child_instance in self.child_instances_for_delete:
                child_instance.delete()
            for field in self.nested_fields:
                for child_serializer in self.child_serializers.get(field, []):
                    if self.nested_fields[field][0]:
                        if getattr(getattr(self.model, field), 'is_generic_relation', None):
                            extra_keys = getattr(self.instance, field).filters
                            for key, value in extra_keys.items():
                                setattr(child_serializer.instance, key, value)
                            setattr(child_serializer.instance, self.nested_fields[field][0], self.instance.pk)
                        else:
                            setattr(child_serializer.instance, self.nested_fields[field][0], self.instance, **kwargs)
                    child_serializer.save(**kwargs)

            serializer_past_save.send(sender=self.model, serializer=self, instance=self.instance)

        if errors.get('pre_post_error'):
            self.raise_validation_error('Error', errors.get('pre_post_error'))
        return self.instance

    def __ref_to_parent(self):
        parent_obj = getattr(self, 'parent_obj', None)
        if parent_obj:
            self.limits_list = parent_obj.limits_list
            self.user = parent_obj.user
            self.view_obj = parent_obj.view_obj

    # برای ولیدیت کردن اطلاعات در سریالایزر در پست و پوت
    def run_validation(self, data=None):
        data = data or {}
        errors = {}
        serializer_pre_validation.send(sender=self.model, serializer=self, instance=self.instance, data=data, errors=errors)
        self.pre_validation(data=data)
        self.__ref_to_parent()
        self.set_limits()
        try:
            for extra_validation in list(self.extra_validations):
                extra_validation(self, data=data,)
            # self.Meta.model.extra_validation(instance=self.instance, data=data)
        except ValidationError as exc:
            errors.update({"extra_validation": as_serializer_error(exc)})

        self.nested_datas = dict()
        for field in self.nested_fields:
            self.nested_datas[field] = data.pop(field, None)

        if isinstance(data, dict):
            extra_fields = [key for key in self.readonly_fields if key in data.keys()]
            if extra_fields and not self.ignore_readonly_fields:
                errors.update({"data_structure":
                                   f"""فیلدهای اضافی در پست: ({', '.join(extra_fields)})--- لیست فیلدهای مجاز:({', '.join(self.writable_fields)})"""})
        if (self.instance and data.get(self.pk_field) and self.instance.pk != data.get(self.pk_field)):
            errors.update({"pk_not_valid": "pk not valid for this request"})

        try:
            data = super().run_validation(data)
        except ValidationError as exc:
            data = {attr: value for attr, value in data.items()
                    if attr in (self.fields - self.nested_fields.keys() - set(self.readonly_fields))
                    and not (self.fields[attr].read_only and not self.model.has_setter(attr))
                    }
            errors.update({"details": as_serializer_error(exc)})

        try:
            self.instance = self.update_instance(data)
        except ValidationError as exc:
            errors.update({"save_errors": as_serializer_error(exc)})
        except Exception as e:
            errors.update({"save_errors": str(e)})

        try:
            data = self.nested_run_validation(data)
        except ValidationError as exc:
            errors.update({"nested_data": as_serializer_error(exc)})
        if errors:
            raise ValidationError(errors)

        serializer_past_validation.send(sender=self.model, serializer=self, instance=self.instance, data=data,errors=errors)
        self.past_validation(data=data)
        return data

    # برای حالت نستد تمام دیتاهای نستد را ولیدیت میکند و همچنین لیستی از سریالایزرهای نستد درست میکند که در زمان سیو به درد میخورد
    def nested_run_validation(self, data=None):
        errors = {}
        data = data or {}
        try:        
            self.child_serializers = dict()
            self.nested_instances = dict()
            self.child_instances_for_delete = list()
            for field in self.nested_fields:
                nested_datas = self.nested_datas[field]
                if not nested_datas or self.fields[field].read_only:
                    continue
                related_name = getattr(self.instance, field, None) if self.instance and self.instance.pk else None
                old_childes = related_name.all() if related_name else None
                child_serializer_class = self.fields[field].child.__class__
                child_pk_field = child_serializer_class.pk_field  # self.nested_fields[field][1]
                child_pk_values = list()
                self.child_serializers[field] = list()
                i = 0
                for nested_data in nested_datas:
                    nested_errors = {}
                    parent_id = nested_data.get(self.nested_fields[field][0] or '_')
                    if parent_id and (not self.instance or self.instance.pk != parent_id):
                        nested_errors.update({"invalid_parent_id": "parent id not valid for some nested items"})
                    child_pk_value = nested_data.get(child_pk_field)
                    if child_pk_value:
                        child_pk_values.append(child_pk_value)
                    child_filter = Q(**{child_pk_field: child_pk_value or -1})
                    child_instance = old_childes.filter(child_filter).first() if old_childes else None
                    if child_pk_value and not child_instance:
                        nested_errors.update({"invalid_child_id": "This child not in previous childes!!"})
                    nested_data.update({"_parent_": self.instance})
                    child_serializer = child_serializer_class(instance=child_instance, data=nested_data)
                    if self.nested_fields.get(field) and self.nested_fields[field][0]:
                        parent_field = child_serializer.fields.get(self.nested_fields[field][0])
                        if parent_field:
                            parent_field.required = False
                    if child_serializer.is_valid():
                        self.child_serializers[field].append(child_serializer)
                    else:
                        nested_errors.update({'validation': child_serializer._errors})
                    if nested_errors:
                        list_nested_errors = errors.get(f"{field}", [])
                        list_nested_errors.append({f"{i}": nested_errors})
                        errors.update({f"{field}": list_nested_errors})
                    i += 1
                if old_childes:
                    self.child_instances_for_delete += [old_child for old_child in
                                                        old_childes.exclude(**{f"{child_pk_field}__in": child_pk_values})]
        except Exception as e:
            errors.update({f"unexpected_error": str(e)})
        if errors:
            raise ValidationError(errors)
        return data

    # برای نمایس اطلاعات توسط سریالایزر در گت
    def to_representation(self, instance, **kwargs):
        # این متد در گت فراخوانی می شود
        # خذف متا دیتا در صورتی که در اینت سریالایزر متا را غیر فعال کرده باشیم (برای افزایش سرعت در گت لیست ایتم های دارای نستند
        # if not self.include_metadata:
        #     fields = [field for field in self.fields]
        #     for field in fields:
        #         if field.__contains__("_meta_data"):
        #             self.fields.pop(field, None)
        #     self.fields.pop('navigation_instances', None)
        #     for field in self.nested_fields.keys():
        #         _field = self.fields.get(field)
        #         if _field:
        #             _field.child.include_metadata = False

        # حذف نستد ها در مواردی که ریلیتد نیم داریم و اینستن نداریم یا پرامری کی ندارد
        # if not self.instance or (not isinstance(self.instance, list) and not getattr(self.instance,'pk', None)):
        serializer_pre_get.send(sender=self.model, serializer=self, instance=instance, **kwargs)
        pre_get_res = self.pre_get(instance=instance, **kwargs)
        if not instance.pk:
            for field in self.nested_fields.keys():
                if self.nested_fields[field][0]:
                    self.fields.pop(field, None)
        self.__ref_to_parent()
        self.set_limits(instance=instance)
        # سوپر متد اصلی
        data = super().to_representation(instance)
        # # data["exx"] = str(self.parent_obj)
        # data["exx2"] = str(self.parent)
        # # data["exx3"] = str(self.parent_obj.instance.pk)
        # data["exx4"] = str(self.parent.instance.pk) if self.parent and  self.parent.instance else 'rr'
        # تغیر وضعیت رکواید بودن یا رید انلی بودن فیلدها در اطلاعات متا بر اساس تغییرات در سریالایزر
        # if self.include_metadata:
        #     data['meta_datas'] = {}
        #     for field in self.fields:
        #         if field.__contains__("_meta_data"):
        #             f = data.pop(field, None)
        #             if f:
        #                 f_name = field.replace("_meta_data", "")
        #                 _field = self.fields.get(f_name)
        #                 if _field:
        #                     has_setter = not self.model.has_setter(f_name)
        #                     f.update({'read_only': _field.read_only and has_setter, 'required': _field.required})
        #                     data['meta_datas'][f_name] = f
        #         if self.nested_fields and field in self.nested_fields:
        #             _field = self.fields.get(field)
        #             data['meta_datas'][field] = {"type": "list",
        #                                          "verbose_name": field,
        #                                          "validators": [],
        #                                          "field_type": "ListSerializer",
        #                                          'required': _field.required,
        #                                          'read_only': _field.read_only}
        #         if self.extra_fields and field in self.extra_fields:
        #             _field = self.fields.get(field)
        #             data['meta_datas'][field] = {"type": "other",
        #                                          "verbose_name": field,
        #                                          "validators": [],
        #                                          "field_type": "Other",
        #                                          'required': _field.required,
        #                                          'read_only': _field.read_only}
        #             # data['meta_datas'][field] = {"type": model_fields_type_map.get(type(field), "other"),
        #             #                             "verbose_name": field.verbose_name,
        #             #                             'required': field.null,
        #             #                             "validators": [validator.__dict__ for validator in field.default_validators],
        #             #                             "field_type": field.get_internal_type(),
        #             #                             # "field_name": field.name
        #             #                             }
        #     # اضافه کردن ابجکت های بلنک به دیتا
        #     # data['blank_objects'] = dict()
        #     # for key, value in self.blank_objects.items():
        #     #     key = key.replace('blank_', '')
        #     #     data['blank_objects'][key] = value.data
        #

        # تغییر نوع داده در مواردی که کویری مستقیم میزنیم و اطلاعات دسیمال و دیت تایم به صورت ابجکت بر میکردند و باید رشته شوند که در سریالایزر خطا ایجاد نکند
        for field, value in data.items():
            if isinstance(value, (date, datetime)):
                data[field] = str(value)
            elif isinstance(value, Decimal):
                data[field] = float(value)

        fields = list(self.fields.keys())
        if self.include_metadata and instance:
            data.update({"meta_datas": instance.get_meta_datas(fields, self.base_limits)}) or {}
            pk = (getattr(instance, 'pk', None) or 0) if instance else 0

            data['meta_datas'].update({"post_url": reverse('dynamic-api-detail',
                                                           kwargs={'pk': pk,
                                                                   'model': f"{self.model._meta.app_label}-{self.model._meta.model_name}"})})

            meta_data_fields = list(data['meta_datas'].keys())
            for field in self.fields:
                if field not in meta_data_fields:
                    _field = self.fields.get(field)
                    data['meta_datas'][field] = {"type": "list" if field in (self.nested_fields or []) else "other",
                                                 "verbose_name": field,
                                                 "validators": [],
                                                 "field_type": "ListSerializer" if field in (
                                                             self.nested_fields or []) else "Other",
                                                 'required': _field.required,
                                                 'readonly': _field.read_only and not self.model.has_setter(field)}

            data['blank_objects'] = {}
            if self.instance and getattr(self.instance, 'pk', None):
                data['navigation_instances'] = getattr(instance, 'navigation_instances', {})
                for field in self.nested_fields.keys():
                    serializer = self.fields[field].child
                    model_instance = serializer.model()
                    data['blank_objects'][f'{field}'] = serializer.to_representation(model_instance)

        if self.include_fks_str and instance:
            data.update({"fk_strs": instance.get_fk_strs(fields)})

        past_get_res = self.past_get(instance=instance, data=data, **kwargs)

        if pre_get_res:
            data.update({"pre_get_res": pre_get_res})
        if past_get_res:
            data.update({"past_get_res": past_get_res})

        serializer_past_get.send(sender=self.model, serializer=self, data=data, instance=instance, **kwargs)
        return data

    # اطلاعات دیتا را در اینستن مقدار دهی میکنیم
    # def update_from_data(self, instance, data):
    #     for field in self.fields - self.nested_fields.keys() - set(self.readonly_fields):
    #         if self.fields[field].read_only and not self.instance.has_setter(field):
    #             continue
    #         value = data.get(field, 'NA')
    #         if not field == self.pk_field and value != 'NA':
    #             try:
    #                 setattr(instance, field, value)
    #             except Exception as e:
    #                 print(str(e))
    #     return instance

    # بر اساس اطلاعات دریافتی و مدل مرتبط اینتنس سریالایزر را مقدار دهی میکنیم
    def update_instance(self, data):
        if not self.instance:
            self.instance = self.model()
        self.instance.initial_data = self.initial_data
        # self.instance = self.update_from_data(self.instance, data)
        self.instance = self.update_instance_from_data(instance=self.instance, validated_data=data)
        return self.instance

    def update_instance_from_data(self, instance, validated_data):
        try:
            raise_errors_on_nested_writes('update', self, validated_data)
            info = model_meta.get_field_info(instance)
            instance.m2m_fields = []

            for attr, value in validated_data.items():
                if attr in info.relations and info.relations[attr].to_many:
                    instance.m2m_fields.append((attr, value))
                    continue  # جلوگیری از setattr روی m2m
                elif value and not isinstance(value, models.Model) and attr in info.relations and info.relations[
                    attr].related_model:
                    related_model = info.relations[attr].related_model
                    # تبدیل ID به اینستنس مدل
                    value = related_model.objects.get(pk=value)

                setattr(instance, attr, value)

            # instance.save()  # ذخیره قبل از set کردن m2mها

            # for attr, value in m2m_fields:
            #     field = getattr(instance, attr)
            #     field.set(value)

            return instance

        except Exception as exc:
            raise  serializers.ValidationError(as_serializer_error(exc))

    # def update_instance_from_data(self, instance, validated_data):
    #     raise_errors_on_nested_writes('update', self, validated_data)
    #     info = model_meta.get_field_info(instance)
    #     m2m_fields = []
    #     for attr, value in validated_data.items():
    #         if attr in info.relations and info.relations[attr].to_many:
    #             m2m_fields.append((attr, value))
    #         else:
    #             setattr(instance, attr, value)
    #     for attr, value in m2m_fields:
    #         field = getattr(instance, attr)
    #         field.set(value)
    #     return instance


class NesteSerializerDefinition:
    def __init__(self, serializer_class: DynamicFieldsModelSerializer, params=None):
        self.serializer_class = serializer_class
        self.params = params or {}
