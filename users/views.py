import json
from http import HTTPStatus

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST

from .models import CustomUser, validate_phone_number
from .sms import send_sms


class HttpResponseNoContent(HttpResponse):
    status_code = HTTPStatus.NO_CONTENT


def get_phone(params):
    phone = params.get('phone', None)
    if phone is None or not validate_phone_number(phone):
        return None
    return phone


def get_params(request):
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
        return request.POST
    elif request.headers['Content-Type'] == 'application/json':
        return json.loads(request.body.decode())
    else:
        raise ValueError("wrong content type")


@require_POST
def request_token(request):
    try:
        params = get_params(request)
    except ValueError:
        return HttpResponseBadRequest()

    phone = get_phone(params)
    if phone is None:
        return HttpResponseBadRequest()

    try:
        user = CustomUser.objects.get(phone=phone)
    except CustomUser.DoesNotExist:
        user = CustomUser(phone=phone)

    user.generate_token()
    msg = 'Authentication code: ' + user.token
    send_sms(user.phone, msg)
    return HttpResponseNoContent()


@require_POST
def login_view(request):
    try:
        params = get_params(request)
    except ValueError:
        return HttpResponseBadRequest()

    phone = get_phone(params)
    token = params.get('token', None)
    if phone is None or token is None:
        return HttpResponseBadRequest()

    user = authenticate(request, phone=phone, token=token)
    if user is None:
        return HttpResponseForbidden()

    login(request, user)
    return HttpResponseNoContent()
