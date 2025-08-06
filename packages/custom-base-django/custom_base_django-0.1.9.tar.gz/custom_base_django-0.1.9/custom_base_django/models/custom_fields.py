import json

from django.db.models import JSONField
from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.functional import cached_property
from django.apps import apps
from django.utils.itercompat import is_iterable
from typing import Dict


class CustomField:
    _extra_field_kwargs = list()

    @staticmethod
    def extra_field_kwargs(model_field, field_kwargs):
        field_kwargs['model_field'] = model_field
        for key in getattr(model_field, "_extra_field_kwargs", []):
            field_kwargs[key] = getattr(model_field, key, None)
        return field_kwargs


class SmartFileListField(JSONField, CustomField):
    _extra_field_kwargs = ['upload_subfolder', 'prefix_file_name']
    def __init__(self, upload_subfolder=None, prefix_file_name=None, *args, **kwargs):
        """
        :param upload_subfolder: if instance has function with this param_value result of function set to upload_subfolder else set fixed value
        :param prefix_file_name: if instance has function with this param_value result of function set to prefix_file_name else set fixed value
        :param args:
        :param kwargs:
        """
        self.upload_subfolder = upload_subfolder
        self.prefix_file_name = prefix_file_name
        super().__init__(*args, **kwargs)

class RelatedIdList:
    def __init__(self, values, model_class, to_field="id", struct_name=None):
        self.values = values or []
        self.model_class = model_class
        self.to_field = to_field
        self.struct_name = struct_name

    @property
    def ids(self):
        return self.values

    def to_list(self):
        return self.values

    def __json__(self):
        return self.to_list()  # یا self.values

    def all(self):
        """
        برگرداندن map از {value: object} به صورت cached
        """
        queryset = self.model_class.objects.filter(**{
            f"{self.to_field}__in": self.values
        })
        return queryset
        # return {getattr(obj, self.to_field): obj for obj in queryset}

    @cached_property
    def objects(self) -> Dict:
        """
        برگرداندن map از {value: object} به صورت cached
        """
        return {getattr(obj, self.to_field): obj for obj in self.all()}

    def to_serializable(self):
        if not is_iterable(self.values):
            raise ValidationError(f"Value must be iterable.")
        result = {"list": list(self.values)}
        serialized_data = {}

        for val in self.values:
            obj = self.objects.get(val)
            if obj:
                if self.struct_name and hasattr(obj, 'get_serializer'):
                    serializer_class = obj.get_serializer(method="get", struct_name=self.struct_name)
                    serialized_data[val] = serializer_class(obj).data
                else:
                    serialized_data[val] = str(obj)
        result.update({"data": serialized_data})
        return result

    def __iter__(self):
        return iter(self.values)

    def __str__(self):
        return str(self.values)

    def __repr__(self):
        return repr(self.to_list())


class RelatedListField(JSONField, CustomField):
    _extra_field_kwargs = ['related_model', 'to_field', 'serializer_struct_name']

    def __init__(self, related_model=None, to_field="id", serializer_struct_name=None, *args, **kwargs):
        self._related_model = related_model
        self.to_field = to_field
        self.struct_name = serializer_struct_name

        kwargs.setdefault('default', list)
        kwargs.setdefault('null', False)
        kwargs.setdefault('blank', True)

        super().__init__(*args, **kwargs)

    @property
    def related_model(self):
        if isinstance(self._related_model, str):
            if '.' in self._related_model:
                self._related_model = apps.get_model(self._related_model)
            else:
                if hasattr(self, 'model'):
                    model_class = self.model
                else:
                    raise ValueError(
                        f"Cannot resolve model '{self._related_model}' without app label. "
                        "Pass model instance or set RelatedListField.model explicitly."
                    )
                app_label = model_class._meta.app_label
                self._related_model = apps.get_model(app_label, self._related_model)

        try:
            field = self._related_model._meta.get_field(self.to_field)
        except Exception:
            raise ValueError(f"Field '{self.to_field}' does not exist on model '{self._related_model._meta.label}'.")

        if not (field.unique or field.primary_key):
            raise ValueError(
                f"Field '{self.to_field}' on model '{self._related_model._meta.label}' must be unique or primary key."
            )

        return self._related_model

    def to_python(self, value):
        model_class = self.related_model

        if value is None:
            value = []

        if isinstance(value, RelatedIdList):
            return value

        if isinstance(value, list):
            ids = value
        else:
            try:
                ids= json.loads(value)
            except (TypeError, json.JSONDecodeError):
                ids = []

        return RelatedIdList(
            ids,
            model_class=model_class,
            to_field=self.to_field,
            struct_name=self.struct_name,
        )

    def from_db_value(self, value, *args):
        if value is None:
            return self.to_python([])
        return self.to_python(value)

    def get_prep_value(self, value):
        if value is None:
            return []
        if isinstance(value, RelatedIdList):
            return value.to_list()
        return value

    def prepare_value(self, value):
        if isinstance(value, RelatedIdList):
            return value.to_list()
        return super().prepare_value(value)

    def validate(self, value, model_instance):
        value = self.to_python(value)
        super().validate(value.to_serializable(), model_instance)

        model_class = self.related_model
        values = value.values

        if not values:
            return

        filter_kwargs = {f"{self.to_field}__in": values}
        count = model_class.objects.filter(**filter_kwargs).count()
        if count != len(values):
            raise ValidationError(f"Some values of '{self.to_field}' do not exist in {model_class._meta.label}.")

    def value_from_object(self, obj):
        val = super().value_from_object(obj)
        if isinstance(val, RelatedIdList):
            return val.to_list()
        return val


class CaseInsensitiveUniqueCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        # اجرای اعتبارسنجی معمولی
        self.unique = False
        super().validate(value, model_instance)
        self.unique = True

        if value:
            # بررسی یونیک بودن بدون حساسیت به کیس
            model_class = model_instance.__class__
            filter_kwargs = {f"{self.attname}__iexact": value.strip()}

            qs = model_class._default_manager.filter(**filter_kwargs)

            # در صورت ویرایش، رکورد فعلی را نادیده بگیر
            if model_instance.pk:
                qs = qs.exclude(pk=model_instance.pk)

            if qs.exists():
                raise ValidationError({
                    self.name: f"This {self.verbose_name or self.name} must be unique (case-insensitive)."
                })

