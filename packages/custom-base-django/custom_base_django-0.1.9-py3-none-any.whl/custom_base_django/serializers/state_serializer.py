from os import access
from django.apps import apps
from ..models.workflow import WorkflowState
from ..models.base import CustomGenericRelation
from ..local_user import get_current_user
from ..utils import first_upper, safe_convert
from types import SimpleNamespace


_meta = SimpleNamespace()
_meta.pk = SimpleNamespace()
_meta.pk.name = "pk"

_state_serializer_classes = dict()


class StateSerializer:
    workflow_state: WorkflowState = None
    nested_serializer_classes = dict()
    # serializers = list()
    _meta = _meta

    @staticmethod
    def get_name(state_name, method):
        serializer_name = f'{first_upper(state_name)}{first_upper(method)}Serializer'
        return serializer_name

    @classmethod
    def get_class_serializer(cls, state, method="get", serializer_struct=None, workflow_serializer=None, request=None):
        if not isinstance(state, WorkflowState):
            return
        class_name = cls.get_name(state_name=state.name, method=method)
        if class_name not in _state_serializer_classes.keys():
            state_class_serializer = type(class_name, (cls,), {})
            state_class_serializer.state = state
            state_class_serializer.request_data = request
            state_class_serializer.parent_workflow_serializer = workflow_serializer
            serializer_struct = serializer_struct or state.serializer_struct or {}
            # {"choice": {"model": "custom_base_django.choice", "to_field": "pk", "access_list":
            #     {[{"groups":[], "users":[], "access_mode":{"readonly":[], "drop":[], "hidden":[], "required":[]},
            #     "nesteds":{"nested1":{"readonly":[], "drop":[], "hidden":[], "required":[]}}}]}},
            #      "product": { }
            #      }
            for key, item in serializer_struct.items():
                app_label, model_name = item.pop("model", "").split(".")
                model = apps.get_model(app_label, model_name)
                class_serializer = model.get_serializer(method=method, struct_name=item.get("struct_name", "default"))

                class_serializer.limits_list = item.get("access_list", [])
                class_serializer.to_field = item.get("to_field", "")

                state_class_serializer.nested_serializer_classes[key] = {"queryset": f"nested_{key}_qs",
                                                                         "class_serializer": class_serializer}
                setattr(state_class_serializer, f"nested_{key}_qs", CustomGenericRelation(model, **item))

            _state_serializer_classes[class_name] = state_class_serializer
        return _state_serializer_classes.get(class_name)

    def __get__(self, instance, owner):
        self.parent = instance
        return self

    def __init__(self, pk=None, user=None, data=None, request=None, ignore_readonly_fields=None):
        self.pk = pk
        self.request = request
        self.serializers = list()
        self.errors = {}
        self._data = data
        self.user = user or get_current_user()
        self.ignore_readonly_fields = ignore_readonly_fields

    def run_validation(self, data=None):
        data = data or self._data or {}
        _errors = {}
        self.serializers = list()
        for key, item in self.nested_serializer_classes.items():
            # instances = item['queryset']
            instances = getattr(self, self.nested_serializer_classes[key]['queryset'], None).all()
            class_serializer = item['class_serializer']
            _data = data.get(key)
            i = 0
            _serializer_errors = dict()
            for instance_data in _data:
                pk_field = class_serializer.pk_field
                if instance_data.get(pk_field) and self.pk is None:
                    _serializer_errors.update({"invalid_data_pk": f"pk not valid for create request!!"})
                    continue
                if not instances and instance_data.get(pk_field):
                    _serializer_errors.update(
                        {"invalid_data_pk": f"This data has invalid pk for this request ({instance_data[pk_field]})!!"})
                    continue
                if instance_data.get(pk_field):
                    instance = instances.filter(**{pk_field: instance_data[pk_field]}).first() if instance_data.get(
                        class_serializer.pk_field) else None  # instances.model()
                else:
                    instance = instances.first() or None  # instances.model()
                _serializer = class_serializer(instance=instance, data=instance_data, ignore_readonly_fields=self.ignore_readonly_fields)
                _serializer.parent_state_serializer = self
                _serializer.request_data = self.request
                if _serializer.is_valid():
                    self.serializers.append(_serializer)
                else:
                    _serializer_errors.update({i: {'validation': _serializer._errors}})
                # self.serializers.append(_serializer)

                i += 1
            if _serializer_errors:
                _errors.update({key: _serializer_errors})

        if _errors:
            self.errors = _errors
            # raise ValidationError(_errors)
        self._data = data
        return data

    def is_valid(self):
        if not self.serializers:
            self.run_validation(self._data)
        return not self.errors

    @property
    def data(self, **kwargs):
        if not self.serializers and self._data:
            self.run_validation(self._data)
        if self.errors:
            return self.errors
        return self.to_representation(**kwargs)

    def to_representation(self, **kwargs):
        data = {}
        for key in self.nested_serializer_classes.keys():
            # instances = self.nested_serializer_classes[key]['queryset'].all()
            if self.pk == '0':
                instances = [getattr(self, self.nested_serializer_classes[key]['queryset'], None).model()]
            else:
                instances = getattr(self, self.nested_serializer_classes[key]['queryset'], None).all()

            serializer_class = self.nested_serializer_classes[key]['class_serializer']
            data[key] = list()
            for instance in instances:
                serializer = serializer_class(instance=instance)
                serializer.parent_state_serializer = self
                serializer.request_data = self.request
                data[key].append(serializer.data)
        return data

    def save(self, **kwargs):
        if self.is_valid():
            for serializer in self.serializers:
                serializer.save(**kwargs)
                if not self.pk:
                    self.pk = getattr(serializer.instance, self.to_field, None)
