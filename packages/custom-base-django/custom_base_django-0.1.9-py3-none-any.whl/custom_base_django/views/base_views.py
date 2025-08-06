import json
from typing import Any

from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.apps import apps
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..local_user import set_current_user
from ..utils import get_variable_setting
from ..tasks import execute_periodic_task
from ..utils import safe_convert

from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuthenticationFromCookie(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        raw_token = self.get_raw_token(header) if header else None

        if raw_token is None:
            raw_token = request.COOKIES.get('access_token')

            if raw_token is None:
                return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError) as e:
            if getattr(request, 'safe_authentication', False):
                request._auth_error = str(e)
                request.user = AnonymousUser()
                return None
            raise e

default_app = get_variable_setting('DEFAULT_APP', 'custom_base_django')

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # اضافه کردن اطلاعات اضافی به توکن
        token['username'] = getattr(user, 'username', None)
        return token

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        data = super().validate(attrs)
        data["access_token"] = data.get("access")
        data["refresh_token"] = data.get("refresh")
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class HelloWorldView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello, World!"})


class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'  # برای تنظیم تعداد آیتم‌ها در هر صفحه از طریق پارامتر URL
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # تعداد کل آیتم‌ها
            'total_pages': self.page.paginator.num_pages,  # تعداد کل صفحات
            'current_page': self.page.number,  # شماره صفحه فعلی
            'next': self.get_next_link(),  # لینک صفحه بعدی
            'previous': self.get_previous_link(),  # لینک صفحه قبلی
            'results': data  # داده‌های صفحه فعلی
        })


class DynamicAPIView(APIView):
    pagination_class = CustomPagination
    authentication_classes = [JWTAuthenticationFromCookie]

    def set_object(self):
        try:
            if self.pk is not None:
                pk_int = safe_convert(self.pk, int)
                if pk_int is None:
                    func = getattr(self.model_class, self.pk, None)
                    if func:
                        self.instance = func(self.request.GET).first()
                        self.pk = self.instance.pk
                elif pk_int > 0:
                    self.instance = self.model_class.objects.get(pk=self.pk)
                else:
                    self.instance = self.model_class()
                self.instance._request = self.request
                for key, value in self.request.GET.items():
                    setattr(
                        self.instance,
                        f"{key}{'_id' if key in self.instance.f_key_fields else ''}",
                        value,
                    )
        except self.model_class.DoesNotExist:
            self.errors = JsonResponse({"message": "Object does not exist!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # هندل عمومی فقط برای مواقع غیرمنتظره
            self.errors =  JsonResponse({"message": "Unexpected error!", "error": str(e)}, status=500)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        set_current_user(request.user)
        self.set_object()

    def get_permissions(self):
        if getattr(self.get_serializer_class(), 'need_authentication', True):
            return [IsAuthenticated()]
        return [AllowAny()]  # دسترسی برای همه کاربران

    def get_model_class(self,model_name):
        try:
            strs = model_name.split('-')
            if len(strs) > 1:
                app_name = strs[0]
                model_name = strs[1]
            else:
                app_name = default_app
                model_name = strs[0]
            return apps.get_model(app_label=app_name, model_name=model_name)
        except (ValueError, LookupError):
            return None

    def get_dynamic_filters(self, valid_fields=None):
        # دریافت تمام فیلدهای مدل
        if self.model_class:
            valid_fields = valid_fields or []
            # استخراج فیلترهای معتبر از پارامترهای URL
            self.filters = Q()
            for key, value in self.request.GET.items():
                if not value:
                    continue
                value = value.strip()
                value_lower = value.lower()
                if value_lower == 'none':
                    value = None
                elif value_lower == "true":
                    value = True
                elif value_lower == "false":
                    value = False
                elif value[0]== "[":
                    value = json.loads(value)
                field_name, _, lookup = key.partition('__')  # بررسی وجود lookup
                field_name = field_name[1:] if field_name[0]=='~' else field_name
                if field_name in valid_fields:
                    lookup_key = f"{field_name}__{lookup}" if lookup else field_name
                    if key[0] == '~':
                        self.filters &= ~Q(**{lookup_key: value})
                    else:
                        self.filters &= Q(**{lookup_key: value})
            return self.filters

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.model_name = kwargs.get('model')
            self.instance = None
            self.model_class = self.get_model_class(self.model_name)
            self.struct_name = request.GET.get('struct_name', 'default')
            self.search_q = request.GET.get('search_q', None)
            self.get_data = True if request.GET.get('get_data', None) != None else False
            self.with_nested = True if request.GET.get('with_nested', "None") != "None" else False
            self.ignore_readonly_fields = True if request.GET.get('ignore_readonly_fields', "None") != "None" else False
            self.order_by = request.GET.get('order_by', '-pk')
            self.must_save = json.loads(request.GET.get('must_save', 'true'))
            self.include_metadata = False if request.GET.get('no_metadata', None) != None else True
            self.get_structure = True if request.GET.get('get_structure', None) != None else False
            self.required_only = True if request.GET.get('required_only', None) != None else False
            self.required_status = True if request.GET.get('required_status', None) != None else False
            self.get_structure = self.get_structure or self.required_only or self.required_status
            self.serializer_class = self.get_serializer_class()
            self.errors = None
            if not self.model_class:
                self.errors = JsonResponse({'error': 'Invalid model name'}, status=status.HTTP_400_BAD_REQUEST)
            self.pk = self.kwargs.get('pk')
        except self.model_class.DoesNotExist:
            self.errors = JsonResponse({'error': 'Invalid object id'}, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_structure(self,):
        serializer = self.serializer_class(self.model_class())
        return Response(serializer.get_structure(self.required_only, self.required_status), status=status.HTTP_200_OK)

    def get_serializer_class(self, method: str = None):
        method = method or self.request.method
        return self.model_class.get_serializer(struct_name=self.struct_name, method=method,)

    def get(self, request, *args, **kwargs):
        if self.errors:
            return self.errors
        if self.get_structure:
            return self.get_serializer_structure()

        # return self.serializer_class.get_json_response(view_obj=self, *args, **kwargs)
        _data, _status = self.serializer_class.get_json_response(view_obj=self, *args, **kwargs)
        return JsonResponse(_data, status=_status, safe=True)

    def post(self, request, *args, **kwargs):
        if self.errors:
            return self.errors
        if self.get_structure:
            return self.get_serializer_structure()

        _data, _status = self.serializer_class.post_json_data(view_obj=self, *args, **kwargs)
        return JsonResponse(_data, status=_status, safe=True)

    def delete(self, request, *args, **kwargs):
        if self.errors:
            return self.errors

        try:
            if request.GET.get('hard_deleted', False) and request.user.is_superuser:
                res, res_status = self.instance.hard_delete()
            else:
                res, res_status = self.instance.delete()
            return JsonResponse(res, status=res_status.get('status'))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


def run_task(request, task_id):
    res = execute_periodic_task(task_id=task_id)
    return JsonResponse(res)