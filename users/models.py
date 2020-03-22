import random
import uuid
import string
from datetime import datetime, timedelta

from django.db import models
from django.db.models.aggregates import Max
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager


TOKEN_LENGTH = 6
TOKEN_VALID_MINUTES = 15


class Category(models.Model):
    slug = models.CharField(max_length=16, blank=False, null=False, unique=True)
    severity = models.IntegerField(blank=True, null=False, default=0)
    recommendation = models.TextField(blank=True, null=True)
    is_separate = models.BooleanField(default=False)

    def __str__(self):
        return self.slug


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = PhoneNumberField(unique=True, blank=False, null=False)
    token = models.CharField(max_length=24, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    sharepermission = models.BooleanField(blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)
    randomized_id = models.CharField(unique=True, max_length=36, default=uuid.uuid4)

    push_id = models.CharField(max_length=64, blank=True, null=True)
    locale = models.CharField(max_length=10, blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)

    _categories = models.ManyToManyField(Category, blank=True)
    _contacts = models.ManyToManyField("self", blank=True, symmetrical=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return str(self.phone)

    def generate_token(self):
        self.token = ''.join(random.choice(string.digits) for _ in range(TOKEN_LENGTH))
        self.token_expiration = timezone.now() + timedelta(minutes=TOKEN_VALID_MINUTES)
        self.save()

    @property
    def category(self):
        return self._categories.filter(is_separate=False).order_by('-severity').first()

    @property
    def separate(self):
        return self._categories.filter(is_separate=True).all()

    @property
    def profile(self):
        heaviest = self.category
        separate = self.separate
        if heaviest is not None:
            export_category = {
                'category': str(heaviest),
                'severity': heaviest.severity,
                'recommendation': heaviest.recommendation,
            }
        else:
            export_category = {'category': None}

        export_separate = {'separate': [{
            'category': str(category),
            'recommendation': category.recommendation,
        } for category in separate ]}

        data = {**export_category, **export_separate, 'sharepermission': self.sharepermission}
        return data

    @profile.setter
    def profile(self, data):
        push_id = data.get('pushNotificationId', None)
        locale = data.get('locale', None)
        if push_id is None or locale is None:
            raise ValueError("bad data")

        try:
            lon = round(float(data.get('lon', None)), 5)
            lat = round(float(data.get('lat', None)), 5)
        except ValueError:
            raise ValueError("bad data")

        self.push_id = push_id
        self.lon = lon
        self.lat = lat
        self.locale = locale

        try:
            self.full_clean(exclude=['password'])
        except ValidationError as e:
            print(e)
            raise ValueError("bad data")

        self.save()

    @property
    def contacts(self):
        contacts = {}
        for contact in self._contacts.filter(sharepermission=True).all():
            heaviest = contact.category
            separate = contact.separate
            if heaviest is not None:
                contacts[str(contact.phone)] = {
                    'category': str(heaviest),
                    'severity': heaviest.severity,
                    'separate': [str(category) for category in separate],
                }
        return contacts

    @contacts.setter
    def contacts(self, contacts_):
        self._contacts.clear()
        users = []
        for contact in contacts_:
            try:
                user = CustomUser.objects.get(phone=contact)
                users.append(user)
            except CustomUser.DoesNotExist:
                pass
        self._contacts.add(*users)

    def set_categories(self, categories_):
        self._categories.clear()
        cats = []
        for cat_id in categories_:
            try:
                cat, _ = Category.objects.get_or_create(slug=cat_id)
                cats.append(cat)
            except Category.DoesNotExist:
                pass
        self._categories.add(*cats)
