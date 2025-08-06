from django.template.base import kwarg_re
from unicodedata import category
from functools import partial
from .base import BaseModelFiscalDelete, BaseModelWitDateNotFiscalDelete
from django.db import models
from django.db.models import QuerySet, Q
from ..utils import Defaults
from .base import BaseModelWitDateNotFiscalDelete
from ..language_utils import translate as _, lang
from django.conf import settings

from functools import  partial


class Choice(BaseModelFiscalDelete):
    def default_translated_title(self):
        return {"fa": "", "en": ""}
    migratable_data = True
    category = models.CharField(max_length=255, verbose_name=_("category"))
    title = models.CharField(max_length=255, verbose_name=_("title"))
    category_title = models.CharField(max_length=255, verbose_name=_("category_title"), unique=True,editable=False, blank=True, null=True)
    # translated_title = models.JSONField(verbose_name=_("translated_title"), blank=True, null=True, default=default_translated_title)
    translated_title = models.JSONField(verbose_name=_("translated_title"), blank=True, null=True, default=partial(Defaults.fix_json,{"fa":"", "en":"",  }))

    # title_en = models.CharField(max_length=255, verbose_name=_("title_en"), null=True, blank=True)
    # title_fa = models.CharField(max_length=255, verbose_name=_("title_fa"), null=True, blank=True)
    # title_bz = models.CharField(max_length=255, verbose_name=_("title_bz"), null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['category', 'title'], name='unique_category_title')
        ]

    @classmethod
    def _get_model_serializer(cls, method: str, struct_name, serializer_base_class=None):
        serializer_base_class = cls.serializer_base_struct.get_serializer_base_class(struct_name=struct_name)
        if struct_name == 'default':
            serializer_base_class.fields = ['category', 'title', 'translated_title']
        return super()._get_model_serializer(method, struct_name, serializer_base_class)
    
    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.category_title = f'{self.category}-{self.title}'
        super().save(*args, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def __str__(self, _lang="en"):
        return f'{self.translated_title.get(lang, self.title) or self.title}'


class CustomForeignKey(models.ForeignKey):
    def __init__(self, to, **kwargs):
        self.old_to_field = kwargs.pop('old_to_field', None)
        super().__init__(to, **kwargs)


class ChoiceForeignKey(CustomForeignKey):
    def __init__(self,
                 limit_title=None,
                 default=None,
                 **kwargs,
                 ):
        """
        :param limit_title: as str from category in choice table( set limit_choice, related_name)
        :param default: as str (title of defult in choice table in this category)
        :param kwargs:
        """
        # if limit_title is None:
        #     raise ValueError("limit_title is required")
        limit_choices_to = kwargs.get('limit_choices_to')
        if limit_title or limit_choices_to:
            kwargs['limit_choices_to'] = limit_choices_to if limit_choices_to else Q(category=limit_title)
        filters = {"category": limit_title}
        if default and isinstance(default, str):
            filters.update({"title": default, })
        kwargs['default'] = kwargs.get("default",
                                       partial(Defaults.first_object, model=Choice, filters=filters))
        kwargs['blank'] = kwargs.get('blank', True)
        kwargs['null'] = kwargs.get('null', True)
        kwargs['on_delete'] = kwargs.get('on_delete', models.SET_NULL)
        if 'related_name' not in kwargs or kwargs['related_name'] is None:
            if limit_title:
                kwargs['related_name'] = f"{limit_title}_choices"
            else:
                kwargs['related_name'] = f"choice_field_{id(self)}"
        kwargs['to_field'] = 'category_title'
        kwargs.pop('to', None)

        super().__init__('custom_base_django.Choice', **kwargs, old_to_field="id")
