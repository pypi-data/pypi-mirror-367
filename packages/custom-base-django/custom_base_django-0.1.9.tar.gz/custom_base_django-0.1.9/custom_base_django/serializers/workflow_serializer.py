from os import access
from django.apps import apps

from .state_serializer import StateSerializer
from ..models import Workflow, WorkflowState, WorkflowHistory
from ..models.base import CustomGenericRelation
from ..utils import first_upper

_workflow_serializer_classes = dict()


class WorkFlowSerializer:
    workflow: Workflow = None
    nested_serializer_classes = dict()
    serializers = list()

    @staticmethod
    def get_name(workflow_name, method):
        serializer_name = f'{first_upper(workflow_name)}{first_upper(method)}Serializer'
        return serializer_name

    @classmethod
    def get_class_serializers(cls, wf_name, method="get"):
        class_name = cls.get_name(workflow_name=wf_name, method=method)
        if class_name not in _workflow_serializer_classes.keys():
            wf_class_serializer = type(class_name, (cls,), {})
            wf_class_serializer.nested_serializer_classes = dict()
            wf_class_serializer.workflow = Workflow.objects.filter(name=wf_name).first()
            wf_class_serializer.all_states = wf_class_serializer.workflow.workflow_states.all().order_by("order_number")
            # wf_class_serializer.workflow_history = WorkflowHistory.objects.filter(
            #     workflow=wf_class_serializer.workflow).order_by('-id')
            wf_class_serializer.wf_history_serializer_class = WorkflowHistory.get_serializer(method=method,
                                                                                             struct_name='workflow_history')
            wf_class_serializer.wf_state_serializer_class = WorkflowState.get_serializer(method=method)
            wf_class_serializer.state_serializers = None
            wf_class_serializer.wf_history_serializer = None
            wf_class_serializer.wf_first_history_serializer = None
            _workflow_serializer_classes[class_name] = wf_class_serializer
        return _workflow_serializer_classes[class_name]

    def __init__(self, object_id=None, user=None, data=None, ignore_readonly_fields=None, request=None,
                 include_metadata=None):
        self.method = getattr(self, 'method', 'get')
        self.object_id = object_id
        self.request = request
        self.user = user
        self.ignore_readonly_fields = ignore_readonly_fields
        workflow_history = WorkflowHistory.objects.filter(
            workflow=self.workflow).order_by('-id')
        self.workflow_history = workflow_history.filter(object_id=object_id)
        # self.workflow_history = self.workflow_history.filter(object_id=object_id)
        last_workflow_history = self.workflow_history.first()
        self.current_state = last_workflow_history.state if last_workflow_history else self.all_states.first()
        self.main_serializers_class = StateSerializer.get_class_serializer(
            state=self.current_state,
            method=self.method, workflow_serializer=self,
            request=self.request
        )
        self.errors = {}
        self._data = data

    def run_validation(self, data=None):
        data = data or self._data or {}
        self.errors = {}
        self.serializers = {}
        try:
            main_data = data.get('main_data', {})
            if main_data:
                self.state_serializers = self.main_serializers_class(pk=self.object_id, data=main_data,
                                                                     user=self.user, request=self.request,
                                                                     ignore_readonly_fields=self.ignore_readonly_fields,
                                                                    )
                self.serializers.update({'main_data': self.state_serializers})

            wf_data = data.get('wf_data', {})
            wf_history_count = self.workflow_history.count()


            if not wf_history_count and (not wf_data or wf_data):
                first_wf_history_instance = WorkflowHistory(workflow=self.workflow, object_id=self.object_id, state=self.current_state,)
                first_wf_history_instance.request_data = self.request
                first_wf_data = wf_data.copy()
                first_wf_data["target_state"] = None
                self.wf_first_history_serializer = self.wf_history_serializer_class(instance=first_wf_history_instance,
                                                                                    data=first_wf_data,
                                                                                    )
                self.serializers.update({'first_wf_data': self.wf_first_history_serializer})

            if wf_data:
                wf_history_instance = WorkflowHistory(workflow=self.workflow, object_id=self.object_id, state=self.current_state)
                wf_history_instance._target_state = wf_data.get('target_state')
                wf_history_instance.request_data = self.request
                self.wf_history_serializer = self.wf_history_serializer_class(instance=wf_history_instance,
                                                                              data=data.get('wf_data', {}),
                                                                              )
                self.serializers.update({'wf_data': self.wf_history_serializer})
            # if not wf_history_count and (not wf_data or (wf_data and wf_data.get('target_state'))):
                
            if self.object_id == 0 and wf_data and not main_data:
                self.errors["main_data"] = "..."


            for key, serializer in self.serializers.items():
                if not serializer.is_valid():
                    self.errors[key] = serializer.errors
        except Exception as e:
            print(e, __file__)

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
        rep_data = {}

        wf_serializer_instance = WorkflowHistory(workflow=self.workflow, object_id=self.object_id,
                                                 state=self.current_state)
        wf_serializer_instance.request_data = self.request

        rep_data["wf_data"] = self.wf_history_serializer_class(instance=wf_serializer_instance).data

        rep_data["wf_history"] = self.wf_history_serializer_class(instance=self.workflow_history, with_nested=False,
                                                              include_metadata=False, many=True).data
        rep_data["wf_states"] = self.wf_state_serializer_class(self.all_states, many=True).data

        rep_data["main_data"] = self.main_serializers_class(pk=self.object_id, user=self.user, request=self.request).data

        return rep_data

    def save(self, **kwargs):
        if self.is_valid():
            main_serializer = self.serializers.get("main_data")
            wf_serializer = self.serializers.get("wf_data")
            first_wf_serializer = self.serializers.get("first_wf_data")
            if main_serializer:
                main_serializer.save(**kwargs)

            if first_wf_serializer :
                if first_wf_serializer .instance.object_id in (None, '0'):
                    first_wf_serializer .instance.object_id = main_serializer.pk
                first_wf_serializer.save(**kwargs)

            if wf_serializer:
                if wf_serializer.instance.object_id in (None, '0'):
                    wf_serializer.instance.object_id = main_serializer.pk
                wf_serializer.save(**kwargs)






