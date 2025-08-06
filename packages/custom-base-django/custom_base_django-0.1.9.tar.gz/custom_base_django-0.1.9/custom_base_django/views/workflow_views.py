from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response

from .base_views import DynamicAPIView
from ..serializers.workflow_serializer import WorkFlowSerializer
from ..utils import safe_convert


class ApiWorkflowView(DynamicAPIView):
    def set_object(self):
        if self.pk is not None:
            pk_int = safe_convert(self.pk, int)
            if pk_int is None:
                func = getattr(self.model_class, self.pk, None)
                if func:
                    self.instance = func(self.request.GET).first()
                    self.pk = self.instance.pk


    def setup(self, request, *args, **kwargs):

        try:
            self.workflow_name = kwargs.get('workflow_name')
            self.workflow_model_class = self.get_model_class('Workflow')
            self.workflow_instance = self.workflow_model_class.objects.filter(name=self.workflow_name).first()
            super().setup(request, *args, **kwargs)

            if self.pk == None:
                self.errors = JsonResponse({'error': 'Invalid object id'}, status=status.HTTP_400_BAD_REQUEST)


        except self.workflow_model_class.DoesNotExist:
            self.errors = JsonResponse({'error': 'Invalid object id'}, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self, method='get'):
        return WorkFlowSerializer.get_class_serializers(self.workflow_name, method=method)

    def get(self, request, *args, **kwargs):
        if self.errors:
            return self.errors
        workflow_serializer = self.serializer_class(object_id=self.pk, user=self.request.user, request=request)

        return JsonResponse(workflow_serializer.data)

    def post(self, request, *args, **kwargs):
        if self.errors:
            return self.errors
        workflow_serializer = self.serializer_class(object_id=self.pk, user=self.request.user,
                                                    data=self.request.data, request=self.request,
                                                    ignore_readonly_fields=self.ignore_readonly_fields,
                                                   )
        if workflow_serializer.is_valid():
            created = not (self.instance and self.instance.pk)
            workflow_serializer.save(**kwargs)
            _status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        else:
            _status = status.HTTP_400_BAD_REQUEST
        context = workflow_serializer.data
        return JsonResponse(context, status=_status, safe=True)
