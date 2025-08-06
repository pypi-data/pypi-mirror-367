
from click.core import F
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import QuerySet, Q
from django.db.models.expressions import RawSQL
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from django.conf import settings
from ..local_user import get_current_user
from ..language_utils import translate as _
from ..serializers.base import NesteSerializerDefinition, DynamicFieldsModelSerializer
from ..utils import FreeField, get_limits, first_upper, Defaults, ClassProperty
from ..managers import CustomActiveUserManager, CustomRelatedNameManager, CustomGenericRelation, CustomManager
from django.core.exceptions import FieldDoesNotExist

"""
    این فایل شامل کلاس‌ها و توابعی است که برای تعریف مدل‌های داده در جنگو استفاده می‌شوند.
    این کلاس‌ها و توابع امکانات مختلفی را برای مدیریت داده‌ها، فیلتر کردن، مرتب‌سازی، و اعتبارسنجی فراهم می‌کنند.

    کلاس‌های اصلی:
    - CustomQuerySet: کلاس کوئری‌ست سفارشی برای فیلتر کردن و مرتب‌سازی داده‌ها.
    - CustomRelatedNameManager: کلاس منیجر سفارشی برای مدیریت روابط بین مدل‌ها.
    - BaseModelFiscalDelete: کلاس مدل پایه برای مدل‌هایی که حذف فیزیکی ندارند.
    - BaseModelWitDateNotFiscalDelete: کلاس مدل پایه برای مدل‌هایی که حذف فیزیکی ندارند و دارای فیلدهای تاریخ ایجاد و به‌روزرسانی هستند.
    - BaseModelNotFiscalDelete: کلاس مدل پایه برای مدل‌هایی که حذف فیزیکی ندارند.
"""
__all__ = ['CustomRelatedNameManager',
           'BaseModelFiscalDelete', 'BaseModelWitDateNotFiscalDelete', 'BaseModelNotFiscalDelete',
           'CustomGenericRelation', "SmartFileListField"]



class Select2FormChoices(models.TextChoices):
    NONE = "None", "None"
    POPUP = "popup", "Popup"
    NEW_TAB = "new_tab", "New Tab"


class BaseModelFiscalDelete(models.Model):
    fiscal_delete = True
    # برای مایگرت کردن دیتا
    migratable_data = False
    truncate_on_migrate_data = False
    # اگر این مدل در یک مدل دیگر به عنوان کلید خارجی باشد مشخص میکند که فرم اضافه کردن یا ویرایش سلکت 2 در فرانت چگونه باشد. پاپ آپ یا در صفحه جدید یا کلا قابل اضاف کردن نباشد
    select_2_form = Select2FormChoices.POPUP
    # کلاس سریالایزر پیش فرض را تعیین میکند
    # SerializerBaseStruct = DynamicFieldsModelSerializer.BaseStruct()
    serializer_base_struct = DynamicFieldsModelSerializer.BaseStruct()
    # منیجر را تغییر می دهد
    objects = CustomManager()

    extra_data_entity_type_name = None
    auto_numbers = []
    title = None
    related_properties = list()
    related_meta_properties = list()
    f_key_fields = list()
    readonly_fields = []
    NesteSerializerDefinition = NesteSerializerDefinition
    is_deleted = False
    get_queryset_all = False
    search_fields = []
    _search_fields_lookup = []
    default_struct = '__str__'
    child_annotate_field = None  # عنوان فیلدی از دیتابیس که به منظور ارجاع به این مدل (در مدلی که به این مدل کلید خارجی دارد) به صورت انوتیت در خروجی مورد استفاده قرار میگیرد
    _meta_datas = {}
    _limits_list = []

    is_active = models.BooleanField(default=True, verbose_name="is_active")

    @classmethod
    def has_field(cls, field_name):
        try:
            cls._meta.get_field(field_name)
            return True
        except FieldDoesNotExist:
            return False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self._limits_list:
            self.__class__._limits_list = []

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self.__class__)

    @classmethod
    def user_has_permission(cls, user=None, perm_type="view"):
        user = user or cls.request_user
        perm_codename = f"{perm_type}_{cls._meta.model_name}"
        perm_full = f"{cls._meta.app_label}.{perm_codename}"
        return user.is_superuser or user.has_perm(perm_full)

    @classmethod
    def get_active(cls, request):
        return

    @classmethod
    def get_limits(cls, user):
        return get_limits(cls._limits_list, user)

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        if self.request_user and not self.request_user.is_anonymous:
            if self.pk is None:
                self.creator_user = self.request_user
            self.updator_user = self.request_user
        super().save(*args, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        for attr, value in getattr(self, 'm2m_fields', []):
            field = getattr(self, attr)
            field.set(value)

    @ClassProperty
    def request_user(cls):
        return get_current_user()

    @classmethod
    def get_search_fields_lookup(cls, depth=0):
        _search_fields_lookup = []
        if not cls.search_fields:
            cls.search_fields = []
            for field in cls._meta.fields:
                if (isinstance(field, (models.CharField, models.TextField, models.JSONField, models.URLField))
                        or (field.is_relation and field.related_model)
                        or field.primary_key):
                    cls.search_fields.append(field.name)

        for field_name in cls.search_fields:
            try:
                field = cls._meta.get_field(field_name)
                if field.is_relation and field.related_model:
                    if depth == 0:
                        model_class = field.related_model
                        if hasattr(model_class, "get_search_fields_lookup"):
                            search_fields_lookup = model_class.get_search_fields_lookup(depth=depth + 1).copy()
                            for search_field_lookup in search_fields_lookup:
                                _search_fields_lookup.append(f"{field_name}__{search_field_lookup}")
                else:
                    _search_fields_lookup.append(f"{field_name}__icontains")
            except Exception as e:
                print(str(e))
        if depth == 0:
            cls._search_fields_lookup = _search_fields_lookup.copy()
        return _search_fields_lookup

    @classmethod
    def search_q(cls, q, custom_query=None, view_obj=None):
        filters = Q()
        if q:
            for search_field_lookup in cls._search_fields_lookup:
                filters |= Q(**{search_field_lookup: q})
        if custom_query:
            if q:
                for field in custom_query.get('select_list', {}):
                    filters |= Q(**{f"{field}__icontains": q})
            queryset = cls.objects.custom_raw(**custom_query, view_obj=view_obj)
        else:
            queryset = cls.objects
        return queryset.filter(filters)

    def add_child_annotate(self, queryset: QuerySet, parent_field: str) -> QuerySet:
        """
        :param queryset: کویری ست مرجع از مدلی که به این مدل کلید خارجی دارد
        :param parent_field: عنوان فیلدی از مدل بالا دست که به این مدل کلید خارجی در آن تعریف شده است
        :return: کویری ست را با فیلد رفرنس شده و به صورت parent_field_text بر میگرداند و به عبارتی یک فیلد با عنوان ترکیبی فیلد پرنت و تکست به کویری ست اضافه می شود
        """
        if self.child_annotate_field:
            return queryset.annotate(
                **{f'{parent_field}_text': RawSQL(f'{parent_field}__{self.child_annotate_field}', [])})
        return queryset

    @classmethod
    def has_setter(cls, prop_name):
        prop = getattr(cls, prop_name, None)
        if isinstance(prop, property):
            return prop.fset is not None  # چک می‌کنیم که setter وجود دارد یا نه
        return False

    @classmethod
    def get_model_fields(cls, method='get'):
        """
        Returns a list of field names for the given model,
        excluding related fields and unnecessary extras.
        """
        is_post = method.lower() == 'post'
        if getattr(cls, '_post_fields', None) is None or getattr(cls, '_get_fields', None) is None:
            cls._post_fields = sorted([field.name for field in cls._meta.get_fields() if not (getattr(field, 'related_name', None) or (is_post and field.editable))])
            cls._get_fields = sorted([field.name for field in cls._meta.get_fields() if not (getattr(field, 'related_name', None))])
        return cls._post_fields if is_post else cls._get_fields

    @classmethod
    def serializer_classes(cls):
        if not getattr(cls, '_serializer_classes', None):
            setattr(cls, '_serializer_classes', dict())
        return cls._serializer_classes

    @classmethod
    def serializer_name(cls, method: str, struct_name='default'):
        model_name = cls._meta.model_name
        app_label = cls._meta.app_label
        serializer_name = f'{first_upper(app_label)}{first_upper(model_name)}{first_upper(struct_name)}{first_upper(method)}Serializer'
        return serializer_name

    @classmethod
    def extra_validation(cls, instance=None, data=None, struct_name='default', **kwargs):
        # raise ValidationError(detail={"data_structure":"error text"}, code=10)
        return data

    def get_data(self, method='get', struct_name=None, include_metadata=False, ignore_readonly_fields=False,
                 with_nested=False):
        struct_name = struct_name or self.default_struct
        if struct_name == '__str__':
            return self.__str__()
        else:
            serializer_class = self.get_serializer(method, struct_name)
            return serializer_class(instance=self, include_metadata=include_metadata,
                                    ignore_readonly_fields=ignore_readonly_fields,
                                    with_nested=with_nested).data

    @classmethod
    def get_serializer(cls, method: str, struct_name='default', ):
        return cls._get_model_serializer(method, struct_name, )

    @classmethod
    def get_serializer_base_class(cls, struct_name='default', ):
        return cls.serializer_base_struct.get_serializer_base_class(struct_name=struct_name)

    @classmethod
    def _get_model_serializer(cls, method: str, struct_name, serializer_base_class=None):
        serializer_name = cls.serializer_name(method, struct_name)
        if serializer_name not in cls.serializer_classes().keys():
            cls.serializer_classes()[serializer_name] = cls.__get_model_serializer(method, serializer_name,
                                                                                   serializer_base_class)
        return cls.serializer_classes().get(serializer_name)

    @classmethod
    def __get_model_serializer(cls, method: str, serializer_name, serializer_base_class=None):
        def get_extra_fields(_fields, _nested_fields):
            if not _fields or _fields == '__all__':
                return {}
            model_fields = [f.name for f in cls._meta.get_fields()] + (_nested_fields or [])
            extra_fields = []
            for field_name in _fields:
                if field_name not in model_fields:
                    extra_fields.append(field_name)

            fields_dict = {
                name: FreeField(required=False, read_only=False if cls.has_setter(name) else True, allow_blank=True,
                                allow_null=True)
                for name in extra_fields
            }
            # for name in extra_fields:
            #     fields_dict[f'get_{name}'] = lambda self, obj, name=name: getattr(obj, name, None)
            return fields_dict

        if not serializer_base_class:
            serializer_base_class = cls.get_serializer_base_class()
        fields = serializer_base_class.fields
        if serializer_base_class.extra_fields or serializer_base_class.exclude_fields or serializer_base_class.readonly_fields:
            fields = fields or cls.get_model_fields()
            fields += serializer_base_class.extra_fields
        if fields and serializer_base_class.nested:
            fields = list(set(list(fields) + list(serializer_base_class.nested.keys())))

        serializer_base_class = serializer_base_class or cls.SerializerBaseStruct()
        # به روز کردن فیلدهای نستد به صورتی که فیلد پرنت در آنها حذف و اختیاری شود
        for field in serializer_base_class.nested:
            if isinstance(serializer_base_class.nested[field], cls.NesteSerializerDefinition):
                prop = getattr(cls(), field)
                params = serializer_base_class.nested[field].params
                if prop is not None:
                    if getattr(prop, 'field', None):
                        params.update({"parent_field": prop.field.name})
                params.update({"many": True})
                params.update({"nested_key": field})
                serializer_base_class.nested.update(
                    {field: serializer_base_class.nested[field].serializer_class(**params)})

        serializer_base_class.model = cls
        serializer_base_class.pk_field = cls._meta.pk.name
        serializer_base_class.extra_non_required_fields.append(cls._meta.pk)
        serializer_base_class.readonly_fields += cls.readonly_fields

        serializer_base_class.extra_non_required_fields += (cls.auto_numbers or []) + list(
            serializer_base_class.nested.keys())
        params = serializer_base_class.to_dict()
        Meta = type('Meta', (), {'model': cls, 'fields': fields if fields else '__all__'})
        params.update({'Meta': Meta})
        params.update(get_extra_fields(fields, list(serializer_base_class.nested.keys())))

        class_serializer = type(serializer_name, (DynamicFieldsModelSerializer,), params)
        serializer = class_serializer()
        serializer.__init_class__()
        return class_serializer

    def get_meta_datas(self, fields=None, base_limits=None, **kwargs):
        if not self._meta_datas:
            self.__class__._meta_datas = {
                name.replace("_meta_data", ""): getattr(self, name)
                for name in dir(self.__class__) if name.endswith('meta_data') and isinstance(getattr(self.__class__, name), property)}
        self._meta_datas = self._meta_datas.copy()
        for field in self.f_key_fields:
            self._meta_datas[field] = getattr(self, f"{field}_meta_data", None)

        if fields:
            meta_data_keys = list(self._meta_datas.keys())
            for field in meta_data_keys:
                if field not in fields:
                    self._meta_datas.pop(field)


        base_limits = base_limits or {}
        for f_name in base_limits.get('readonly',[]):
            self._meta_datas[f_name]['readonly'] = True

        for f_name in base_limits.get('required',[]):
            self._meta_datas[f_name]['required'] = True

        for f_name in base_limits.get('hidden',[]):
            self._meta_datas[f_name]['hidden'] = True

        return self._meta_datas

    def get_fk_strs(self, fields):
        return {
            name: getattr(self, f"{name}_str")
            for name in self.f_key_fields}

    @classmethod
    def raise_validation_error(cls, title="error", text="Some errors occurred!", code=1):
        raise ValidationError({title: text}, code=code)

    def __str__(self):
        title = self.title or getattr(self, 'full_name', '')
        code = getattr(self, 'code', '')
        code = f"(code: {code})" if code else ''
        number = getattr(self, 'number', '')
        number = f"(number: {number})" if number else ''
        address = getattr(self, 'address', '')
        address = f"(code: {address})" if address else ''
        return f"{title or code or number or address or ''}" or ''

    @property
    def navigation_instances(self):
        if self.pk:
            _first = self.__class__.objects.order_by('pk').first()
            _last = self.__class__.objects.order_by('pk').last()
            _previous = self.__class__.objects.filter(pk__lt=self.pk).order_by('pk').last()
            _next = self.__class__.objects.filter(pk__gt=self.pk).order_by('pk').first()
        else:
            _first = _last = _previous = _next = None
        return {
            "first": _first.pk if _first else None,
            "previous": _previous.pk if _previous else None,
            "self": self.pk,
            "next": _next.pk if _next else None,
            "last": _last.pk if _last else None,
        }

    def is_changed(self, compare_keys=None):
        if not self.pk:
            return True
        try:
            old_obj = self.__class__.objects.get(pk=self.pk)
        except self.__class__.DoesNotExist:
            return True
        new, old = self.__dict__, old_obj.__dict__
        for k, v in new.items():
            if not compare_keys or k in compare_keys:
                try:
                    if v != old[k]:
                        return True
                except KeyError as e:
                    print(f'key error: {k} ', e.__traceback__.tb_lineno, e)
                    return True
                except TypeError as e:
                    print('TypeError: ', e.__traceback__.tb_lineno, e)
                    return True
        return False

    class Meta:
        abstract = True


class BaseModelNotFiscalDelete(BaseModelFiscalDelete):
    fiscal_delete = False
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True

        self.save(update_fields=['is_deleted'])
        # return f'Object with pk ({self.pk}) was logically deleted.', status.HTTP_200_OK
        return 1, {f'{self._meta.app_label}.{self._meta.model_name}':1}

    def hard_delete(self):
        super().delete()
        return f'object with pk ({self.pk}) deleted', status.HTTP_204_NO_CONTENT

    def restore(self):
        self.is_deleted = False
        self.save(update_fields=['is_deleted'])
        return f'object with pk ({self.pk}) restored', status.HTTP_204_NO_CONTENT

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
            **kwargs
    ):
        super().save(*args, force_insert=force_insert, force_update=force_update, using=using,
                     update_fields=update_fields)

    class Meta:
        abstract = True


class BaseModelWitDateNotFiscalDelete(BaseModelNotFiscalDelete):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    readonly_fields = ['created_at', 'updated_at']

    class Meta:
        abstract = True


class BaseModelContentType:
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    as_table = 'templates/core/partial/table.html'
    as_list = 'templates/core/partial/list.html'

    class Meta:
        abstract = True


class BaseUserTrackable(BaseModelWitDateNotFiscalDelete):

    creator_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True,
                                     related_name='%(app_label)s_creator_%(model_name)s',
                                     verbose_name=_('creator_user'), )
    editor_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True,
                                    related_name='%(app_label)s_updator_%(model_name)s',
                                    verbose_name=_('updator_user'))


    class Meta:
        abstract = True

    def save(self,*args, **kwargs):
        try:
            user = get_current_user()
            if user and not user.is_anonymous:
                if not self.creator_user_id:
                    self.creator_user = user
                self.editor_user = user
            super().save(*args, **kwargs)
        except Exception as e:
            raise e


class BaseActiveUser(BaseUserTrackable):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True,  related_name='%(model_name)s_user',)

    objects = CustomActiveUserManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            if hasattr(self, 'user') and getattr(self, 'user', None) is None:
                current_user = get_current_user()
                if current_user and not current_user.is_anonymous:
                    self.user = current_user
            super().save(*args, **kwargs)
        except Exception as e:
            raise e
