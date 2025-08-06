from .local_user import set_current_user
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.urls import resolve, Resolver404

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_user(request.user)
        response = self.get_response(request)
        return response


class AppendSlashExceptionHandlerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # فقط اگر اسلش آخر نداره و POST هست
        if (
            settings.APPEND_SLASH and
            request.method == 'POST' and
            not request.path.endswith('/')
        ):
            try:
                # چک کنیم اگر اسلش اضافه می‌کردیم URL معتبر می‌شد
                resolve(request.path + '/')
                return JsonResponse(
                    {
                        "error": "Trailing slash required for POST requests.",
                        "detail": f"Did you mean {request.path + '/'} ?"
                    },
                    status=400
                )
            except Resolver404:
                pass  # URL + '/' هم وجود نداره، بذار خودش خطا بده
        return None