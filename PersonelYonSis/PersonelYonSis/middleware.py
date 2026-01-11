from django.shortcuts import redirect
from django.conf import settings
import threading

_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

def get_current_user():
    req = get_current_request()
    if req and hasattr(req, 'user'):
        return req.user
    return None

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Thread-local'a request'i kaydet
        _thread_locals.request = request

        # API endpointleri için login gerekmesin
        if request.path.startswith('/ik_core/api/'):
            return self.get_response(request)
        # kdhold uygulamasındaki url'ler için login gerekmesin
        if request.path.startswith('/kdhold/'):
            return self.get_response(request)
        if not request.user.is_authenticated and request.path not in [settings.LOGIN_URL, '/password_reset/', '/register/']:
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
        # mercis696 için login gerekmesin
        if request.path.startswith('/mercis696/'):
            return self.get_response(request)
