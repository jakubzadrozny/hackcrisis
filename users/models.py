import random
import string
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from .managers import CustomUserManager


TOKEN_LENGTH = 6
TOKEN_VALID_MINUTES = 15


def validate_phone_number(phone):
    return len(phone) >= 9 and len(phone) <= 12 and all([c in string.digits for c in phone[1:]])


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(unique=True, max_length=12, blank=False, null=False)
    token = models.CharField(max_length=24, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)

    is_verified = models.BooleanField(blank=False, null=False, default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)

    push_id = models.CharField(max_length=10, blank=True, null=True)
    locale = models.CharField(max_length=10, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    _contacts = models.ManyToManyField("self", blank=True, symmetrical="False")

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.phone

    def generate_token(self):
        self.token = ''.join(random.choice(string.digits) for _ in range(TOKEN_LENGTH))
        self.token_expiration = timezone.now() + timedelta(minutes=TOKEN_VALID_MINUTES)
        self.save()

    @property
    def profile(self):
        data = {
            'status': 'dupa',
            'category': '1',
        }
        return data

    @profile.setter
    def profile(self, data):
        push_id = data.get('pushNotificationId', None)
        lon = data.get('lon', None)
        lat = data.get('lat', None)
        locale = data.get('locale', None)
        if push_id is None or lon is None or lat is None or locale is None:
            raise ValueError("bad data")

        self.push_id = push_id
        self.lon = lon
        self.lat = lat
        self.locale = locale

        self.save()

    @property
    def contacts(self):
        return [contact.phone for contact in self._contacts.only('phone')]

    @contacts.setter
    def contacts(self, contacts_):
        for contact in contacts_:
            try:
                user = CustomUser.objects.get(phone=contact)
            except user.DoesNotExist:
                raise ValueError("bad data")

        self.contacts_.clear()
        for contact in contacts_:
            user = CustomUser.objects.get(phone=contact)
            self.contacts_.add(user)
