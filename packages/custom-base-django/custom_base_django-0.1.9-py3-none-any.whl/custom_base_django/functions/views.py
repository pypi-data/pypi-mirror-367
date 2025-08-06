from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# from cus.function_registry import registry
import json
import logging
from django.http import JsonResponse
from ..functions.function_registry import registry
from .permissions import HasFunctionPermission
from ..local_user import set_current_user
from ..models.base import CustomManager
from ..utils import add_session_cookie, add_token_cookies
from ..views.base_views import JWTAuthenticationFromCookie

logger = logging.getLogger(__name__)

def custom_serializer(obj):
    if isinstance(obj, datetime):
        # تبدیل datetime به رشته با فرمت ISO
        return obj.isoformat()
    if isinstance(obj, CustomManager):
        return  obj.get_data()
    try:
        return str(obj)  # تلاش برای تبدیل به دیکشنری
    except AttributeError:
        raise TypeError(f"Type {type(obj)} not serializable")


# class FunctionAPIView(APIView):
#     # permission_classes =  HasFunctionPermission
#     registry = registry
#
#     def post(self, request, function_name):
#         func = self.registry.get_function(function_name)
#         if not func:
#             return Response(
#                 {'error': f'Function "{function_name}" not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#         try:
#             data = json.loads(request.body) if request.body else {}
#         except json.JSONDecodeError:
#             return Response(
#                 {'error': 'Invalid JSON data'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         metadata = self.registry.get_metadata(function_name)
#         missing_params = [
#             p for p in metadata['required']
#             if p not in data
#         ]
#
#         if missing_params:
#             return Response(
#                 {
#                     'error': 'Missing required parameters',
#                     'missing': missing_params,
#                     'required': metadata['required']
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         logger.info(f"User {request.user.username} calling {function_name} with data: {data}")
#
#         try:
#             result = func(**data)
#             logger.info(f"Function {function_name} executed successfully")
#             return JsonResponse(json.loads(json.dumps({"result": result},  default=custom_serializer, ensure_ascii=False)))#json.dumps(data, default=str, ensure_ascii=False, indent=4))
#         except Exception as e:
#             logger.error(f"Error in {function_name}: {str(e)}", exc_info=True)
#             return Response(
#                 {'errors': [str(e)]},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


class FunctionAPIView(APIView):
    authentication_classes = []
    registry = registry

    @staticmethod
    def validate_missing(data, metadata):
        return [p for p in metadata['required'] if p not in data]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_current_user(request.user)

    @staticmethod
    def execute_function(func, data, function_name, request):
        logger.info(f"User {request.user.username} calling {function_name} with data: {data}")

        try:
            data.pop('request', None)

            result = func(**data, request=request)
            logger.info(f"Function {function_name} executed successfully")

            status_code = result.get('status_code', 200) if isinstance(result, dict) else 200

            response = JsonResponse(
                json.loads(json.dumps(result, default=custom_serializer, ensure_ascii=False)),
                status=status_code
            )

            if isinstance(result, dict):
                session_id = result.get('session_id')
                if session_id:
                    add_session_cookie(response, session_id)
                if isinstance(result.get('data'), dict):
                    # tokens = result.get('data')
                    # tokens.pop('message', None)
                    # for value in tokens.values():
                    #     response.set_cookie(**value)
                    add_token_cookies(response, result['data'])

            return response

        except Exception as e:
            logger.error(f"Error in {function_name}: {str(e)}", exc_info=True)
            return Response(
                {'errors': [str(e)]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def custom_setup(self, request,*args, **kwargs):
        # super().setup(request, *args, **kwargs)
        function_name = kwargs.get('function_name')
        data = kwargs.get('data', {})
        func = self.registry.get_function(function_name)
        if not func:
            return Response({'error': f'Function "{function_name}" not found'}, status=404)

        metadata = self.registry.get_metadata(function_name)

        allowed_methods = metadata.get('methods', ['GET', 'POST'])
        if request.method not in allowed_methods:
            return Response(
                {'error': f'Method {request.method} not allowed for {function_name}'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        permission = metadata.get('permission', 'authenticated')
        if permission != 'anonymous':
            request.user = JWTAuthenticationFromCookie().authenticate(request)[0]

        if request.method not in allowed_methods:
            return Response(
                {'error': f'Method {request.method} not allowed for {function_name}'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        missing_params = self.validate_missing(data, metadata)

        if missing_params:
            return Response(
                {
                    'error': 'Missing required parameters',
                    'missing': missing_params,
                    'required': metadata['required']
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return self.execute_function(func, data, function_name, request)

    def get(self, request, function_name):
        data = request.query_params.dict()
        return self.custom_setup(request=request, function_name=function_name, data=data)

    def post(self, request, function_name):
        try:
            data = json.loads(request.body) if request.body else request.data
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.custom_setup(request=request, function_name=function_name, data=data)


class FunctionMetadataView(APIView):
    registry = registry

    def get(self, request, function_name=None):
        if function_name:
            metadata = self.registry.get_metadata(function_name)
            if not metadata:
                return Response(
                    {'error': 'Function not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(metadata)
        else:
            return Response(self.registry.get_metadata())