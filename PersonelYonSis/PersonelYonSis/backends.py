from django.contrib.auth.backends import BaseBackend
from .models import User

class CustomUserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Username=username)
            if user.password == password:  # Şifre hash olmadan geçici kontrol
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
