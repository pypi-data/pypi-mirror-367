
from django.apps import AppConfig
from .utils import add_dynamic_property
from django.conf import settings
import warnings


class CustomBaseDjango(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_base_django'

    def ready(self):
        add_dynamic_property()
        from . import functions

        middleware_path = 'custom_base_django.middleware.AppendSlashExceptionHandlerMiddleware'
        if middleware_path not in getattr(settings, 'MIDDLEWARE', []):
            warnings.warn(
                f"{middleware_path} is not in MIDDLEWARE. Consider adding it to handle APPEND_SLASH RuntimeError."
            )

        # from .serializers.base import DynamicFieldsModelSerializer
        # class XTR:
        #     base = DynamicFieldsModelSerializer.BaseStruct()
        # x = XTR()
        # x.base.get_serializer_base_class("default")

        # from .models.choices import Choice
        # Choice.serializerBaseStruct.get_serializer_base_class('default')
