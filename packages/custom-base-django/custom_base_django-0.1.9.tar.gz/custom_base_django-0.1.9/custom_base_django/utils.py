import hashlib
import importlib
import json

from django.db.models import Q
from django.db import models
from django.conf import settings

from django.utils.timezone import now
from datetime import timedelta, datetime
from rest_framework.fields import CharField
import jdatetime
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
__all__ = ['Defaults', ]

from rest_framework.serializers import ListSerializer


def safe_convert(value, convert_type, default=None):
    try:
        return convert_type(value)
    except Exception as e:
        return default

def get_user_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        hash_ip = hashlib.sha256(ip.encode('utf-8')).hexdigest()
        return hash_ip
    except Exception as e:
        raise e

from functools import wraps
def rate_limit(action_key, max_requests, window_seconds, block_seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            id_key = self.ip or self.session_id
            limit_key = f"{action_key}_request_count:{id_key}"
            block_key = f"{action_key}_blocked:{id_key}"

            if cache.get(block_key):
                return False, f"You are temporarily blocked from {action_key.replace('_', ' ')}. Please try later."


            count = cache.get(limit_key, 0)
            if count >= max_requests:
                cache.set(block_key, True, timeout=block_seconds)
                return False, f"Too many {action_key.replace('_', ' ')} requests. You are now temporarily blocked."


            cache.set(limit_key, count + 1, timeout=window_seconds)
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def add_session_cookie(response, session_id, max_age=60*60*24):
    if session_id:
        response.set_cookie(
            'sessionid',
            session_id,
            httponly=True,
            samesite='Lax',
            max_age=max_age
        )
    return response

def add_token_cookies(response, tokens: dict):
    if tokens:
        tokens.pop('message', None)

        for value in tokens.values():
            response.set_cookie(**value)

    return response


class Defaults:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def now(self):
        time_delta_days = self.kwargs.get('time_delta_days', 0)
        return now() + timedelta(days=time_delta_days)  #.strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def now_with_delta(days=0, hours=0, minutes=0, seconds=0):
        return now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)  #.strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def fix_json(m_dict):
        return m_dict

    def object(self):
        try:
            model = self.kwargs.get('model', None)
            filters = self.kwargs.get('filters', {})
            return model.objects.filter(filters).first() if model else None
        except:
            return None

    @staticmethod
    def first_object(model, filters=None, order_by=None):
        try:
            filters = filters or {}
            if isinstance(filters, dict):
                if order_by:
                    return model.objects.filter(**filters).order_by(order_by).first() if model else None
                else:
                    return model.objects.filter(**filters).first() if model else None
            else:
                if order_by:
                    return model.objects.filter(filters).order_by(order_by).first() if model else None
                else:
                    return model.objects.filter(filters).first() if model else None
        except:
            return None


def get_variable_setting(variable_name, default):
    return getattr(settings, variable_name, default)


def get_all_subclasses(cls):
    subclasses = set()

    def _recurse(sub):
        for subclass in sub.__subclasses__():
            if not getattr(subclass._meta, 'abstract', False):
                subclasses.add(subclass)
            _recurse(subclass)

    _recurse(cls)
    return list(subclasses)


def q_to_dict(q_obj):
    result = {}
    for key, value in q_obj.children:
        if isinstance(value, Q):
            result[key] = q_to_dict(value)
        else:
            result[key] = value
    return result


model_fields_type_map = {models.CharField: "string", models.IntegerField: "int", models.DecimalField: "float",
                         models.FloatField: "float",
                         models.BooleanField: "bool", models.DateField: "date", models.DateTimeField: "date_time",
                         list: "list", ListSerializer: "list"}


def get_meta_data(self, field_name):
    field = self._meta.get_field(field_name)
    res = {"type": model_fields_type_map.get(type(field), "other"), "verbose_name": field.verbose_name,
           'required': field.null,
           "validators": [validator.__dict__ for validator in field.default_validators],
           "field_type": field.get_internal_type(),
           "hidden": False,
           "readonly": False,
           # "field_name": field.name
           }
    if field.is_relation and field.related_model:
        model = field.related_model
        limit_to = field._limit_choices_to or {}
        objs = model.objects.filter(limit_to or Q())
        related_field = field.to_fields[0] or 'id'
        if not isinstance(limit_to, dict):
            limit_to = q_to_dict(limit_to)
        if model.has_field("user") and self.has_field("user"):
            limit_to.update({"user": getattr(self, 'user', None)})
        obj = getattr(self, field_name, None)
        str_or_data = 'get_data' if hasattr(obj, 'get_data') else '__str__'
        if obj:
            res.update({"default": {"id": getattr(obj, related_field, None), "value": getattr(obj, str_or_data)()}})
        else:
            res.update({"default": {"id": None, "value": None}})
        if objs.count() <= -1:
            res.update({"type": "list",
                        "choice": [{"id": getattr(obj, related_field, None), "value": getattr(obj, str_or_data)()} for
                                   obj in objs]})
        else:
            base_url = reverse('dynamic-api-list',kwargs={'model': f"{model._meta.app_label}-{model._meta.model_name}"})
            res.update({"type": "select_2", "url":f"{base_url}?{'&'.join(f'{key}={value}' for key, value in limit_to.items())}&{f'to_field={related_field}' if related_field != 'id' else ''}"})
        res.update({"select_2_form": getattr(model,'select_2_form','popup')})

    return res


def add_dynamic_property():
    from .models.base import BaseModelFiscalDelete as Model
    all_subclasses = get_all_subclasses(Model)
    for cls in all_subclasses:
        def make_str_property(f):
            def get_str(obj):
                f_obj = getattr(obj, f.name, None)
                return f_obj.__str__() if f_obj else None

            return property(
                lambda self: get_str(self))  #getattr(self, f.name).__str__() if getattr(self, f.name) else None)

        def make_meta_data_property(f):
            return property(lambda self: get_meta_data(self, f.name))

        setattr(cls, 'related_properties', list())
        setattr(cls, 'related_meta_properties', list())
        setattr(cls, 'f_key_fields', list())
        for field in cls._meta.fields:
            # field meta_data
            property_name = f"{field.name}_meta_data"
            setattr(cls, property_name, make_meta_data_property(field))
            cls.related_meta_properties.append(property_name)

            if field.is_relation and field.related_model in all_subclasses:
                property_name = f"{field.name}_str"
                setattr(cls, property_name, make_str_property(field))
                cls.related_properties.append(property_name)
                cls.f_key_fields.append(field.name)

        cls.get_search_fields_lookup(depth=0)


def get_date(date_str, from_calendar="jalali"):
    if from_calendar.lower() == "jalali":
        year, month, day = map(int, date_str.split('-'))
        return jdatetime.date(year, month, day).togregorian()
    else:
        return datetime.strptime(date_str, "%Y-%m-%d")


def filter_json_to_Q(json):
    if not json.get("filters"):
        return Q(**json)
    filters_json = json.get("filters")
    filters_q = Q()
    for key, value in filters_json.get('conditions', {}).items():
        if filters_json.get('operator', '&'):
            filters_q &= filter_json_to_Q({key: value})
        elif filters_json.get('operator', '|'):
            filters_q |= filter_json_to_Q({key: value})
    return filters_q


class FreeField(CharField):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


def get_limits(limits_list, user, nested_key='', base_limits=None):
    limits = base_limits or {"readonly": [], "drop": [], "hidden": [], "required": []}
    if not limits_list or not user:
        return limits
    for limits_dict in limits_list:
        groups = limits_dict.get('groups', [])
        users = limits_dict.get('users', [])
        user_match = user.groups.filter(name__in=groups).exists() or user.pk in users
        if user_match:
            if nested_key:
                limits["readonly"] += limits_dict.get('access_mode').get('nesteds', {}).get(nested_key, {}).get('readonly', [])
                limits["drop"] += limits_dict.get('access_mode').get('nesteds', {}).get(nested_key, {}).get('drop', [])
                limits["hidden"] += limits_dict.get('access_mode').get('nesteds', {}).get(nested_key, {}).get('hidden', [])
                limits["required"] += limits_dict.get('access_mode').get('nesteds', {}).get(nested_key, {}).get('required', [])
            else:
                limits["readonly"] += limits_dict.get('access_mode').get('readonly', [])
                limits["drop"] += limits_dict.get('access_mode').get('drop', [])
                limits["hidden"] += limits_dict.get('access_mode').get('hidden', [])
                limits["required"] += limits_dict.get('access_mode').get('required', [])

    for mode in limits.keys():
        limits[mode] = list(set(limits[mode]))
    return limits


def first_upper(text: str):
    return f"{text[:1].upper()}{text[1:].lower()}"


class ClassProperty(property):
    def __get__(self, instance, owner):
        return self.fget(owner)


def execute_action_from_function(module_path, **kwargs):
    try:
        module_path, method = module_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
    except ImportError:
        raise ImportError(f" {module_path} Not found!!")
    try:
        method_func = getattr(module, method)
        if callable(method_func):
            return method_func(state=kwargs.pop('state'), **kwargs)
    except AttributeError:
        raise AttributeError(f" {method} in {module_path} Not found!!")
