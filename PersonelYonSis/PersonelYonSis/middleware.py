from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Giriş yapılmamış ve login sayfasında değilse
        if not request.user.is_authenticated and request.path not in [settings.LOGIN_URL, '/password_reset/', '/register/']:
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)