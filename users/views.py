import json
from http import HTTPStatus

from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_POST

from .models import CustomUser
from .sms import send_sms


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

    phone = params.get('phone', None)
    try:
        user = CustomUser.objects.get(phone=phone)
    except CustomUser.DoesNotExist:
        user = CustomUser(phone=phone)
        try:
            user.full_clean()
        except ValidationError:
            return HttpResponseBadRequest()

    user.generate_token()
    msg = 'Authentication code: ' + user.token
    send_sms(str(user.phone), msg)
    return HttpResponse()


@require_POST
def login_view(request):
    try:
        params = get_params(request)
    except ValueError:
        return HttpResponseBadRequest()

    phone = params.get('phone', None)
    token = params.get('token', None)
    if phone is None or token is None:
        return HttpResponseBadRequest()

    user = authenticate(request, phone=phone, token=token)
    if user is None:
        return HttpResponseForbidden()

    login(request, user)
    return HttpResponse()
