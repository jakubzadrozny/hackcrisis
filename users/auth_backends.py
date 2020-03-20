from django.contrib.auth.backends import BaseBackend
from django.utils import timezone

from .models import CustomUser


class TokenBackend(BaseBackend):
    def authenticate(self, request, phone, token):
        try:
            user = CustomUser.objects.get(phone=phone)
        except CustomUser.DoesNotExist:
            return None

        if not user.token_expiration or timezone.now() > user.token_expiration:
            return None

        return user if user.token == token else None


    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
