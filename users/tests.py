from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from .models import CustomUser


class UserTestCase(TestCase):
    def setUp(self):
        self.user = User(phone='123456789')

    def profile_setter_bad_data(self):
        data = {
            'lat': 23.213,
            'lon': 23.231,
            'locale': 'dupa',
        }
        with self.assertRaises(ValidatioError):
            self.user.profile = data


class RequestTokenTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        CustomUser.objects.create(phone='123456789')

    def test_get_not_allowed(self):
        response = self.client.get('/auth/request_token')
        self.assertEqual(response.status_code, 405)

    def test_empty_post(self):
        response = self.client.post('/auth/request_token', {})
        self.assertEqual(response.status_code, 400)

    def test_invalid_phone(self):
        response = self.client.post('/auth/request_token', {'phone': 'dupa'})
        self.assertEqual(response.status_code, 400)

    def test_generates_token_for_existing_user(self):
        phone = '123456789'
        user = CustomUser.objects.get(phone=phone)
        # user = CustomUser(phone=phone)
        # user.save()
        # self.assertFalse(user.token)
        # self.assertEqual(CustomUser.objects.filter(phone=phone).count(), 1)
        #
        # response = self.client.post('/auth/request_token', {'phone': phone})
        #
        # user.refresh_from_db()
        # self.assertTrue(user.token)

    def test_creates_new_user(self):
        phone = '123456789'
        self.assertEqual(CustomUser.objects.filter(phone=phone).count(), 0)

        response = self.client.post('/auth/request_token', {'phone': phone})

        self.assertEqual(CustomUser.objects.filter(phone=phone).count(), 1)
        user = CustomUser.objects.get(phone=phone)
        self.assertTrue(user.token)


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_not_allowed(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 405)

    def test_no_token(self):
        response = self.client.post('/auth/login', {'phone': '123456789'})
        self.assertEqual(response.status_code, 400)

    def test_invalid_phone(self):
        response = self.client.post('/auth/login', {'phone': 'dupa', 'token': 'asd'})
        self.assertEqual(response.status_code, 400)

    def test_invalid_credentials(self):
        user = CustomUser(phone='123456789')
        user.generate_token()

        response = self.client.post('/auth/login', {'phone': '123456789', 'token': '654321'})

        self.assertEqual(response.status_code, 403)

    def test_token_not_requested(self):
        user = CustomUser(phone='123456789')
        user.save()

        response = self.client.post('/auth/login', {'phone': '123456789', 'token': ''})

        self.assertEqual(response.status_code, 403)

    def test_credentials_ok(self):
        user = CustomUser(phone='123456789')
        user.generate_token()
        token = user.token

        response = self.client.post('/auth/login', {'phone': '123456789', 'token': token})

        self.assertEqual(response.status_code, 204)

    def test_expired_token(self):
        user = CustomUser(phone='123456789')
        user.generate_token()
        user.token_expiration = timezone.now() - timedelta(minutes=20)
        user.save()
        token = user.token

        response = self.client.post('/auth/login', {'phone': '123456789', 'token': token})

        self.assertEqual(response.status_code, 403)
