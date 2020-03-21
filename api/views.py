import json
from http import HTTPStatus

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from .models import Questionnaire, Submission


def walk_tree(t, p):
    for key in p:
        if type(t) is not dict or not key in t:
            raise ValueError()
        t = t[key]

    if type(t) is not dict or (not 'category' in t and not 'risk' in t):
        raise ValueError()
    return t.get('category', None) or t.get('risk', None)


def calculate_categories(q, s):
    q = json.loads(q)
    paths = [a.split('.') for a in s]
    categories = [walk_tree(q, p) for p in paths]
    return categories


def get_params(request):
    if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
        return request.POST
    elif request.headers['Content-Type'] == 'application/json':
        return json.loads(request.body.decode())
    else:
        raise ValueError("wrong content type")


@require_GET
def questionnaire(request):
    q = Questionnaire.objects.order_by('-date_created').first()
    return HttpResponse(q.content, content_type='application/json')


@require_POST
def submission(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    user = request.user
    params = get_params(request)
    data = params.get('data', None)
    if data is None or 'result' not in data:
        return HttpResponseBadRequest()

    q = Questionnaire.objects.order_by('-date_created').first()
    try:
        categories = calculate_categories(q.content, data['result'])
    except ValueError:
        return HttpResponseBadRequest()

    submission = Submission(questionnaire=q, user=user, content=data)
    submission.save()
    user.set_categories(categories)
    return HttpResponse()


@require_http_methods(["GET", "POST"])
def profile(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    user = request.user

    if request.method == "GET":
        return JsonResponse(user.profile)

    params = get_params(request)
    data = params.get('data', None)
    if data is None:
        return HttpResponseBadRequest()

    try:
        user.profile = data
    except ValueError:
        return HttpResponseBadRequest()

    return HttpResponse()


@require_http_methods(["GET", "POST"])
def contacts(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    user = request.user

    if request.method == "GET":
        return JsonResponse({'contacts': user.contacts})

    params = get_params(request)
    contacts = params.get('data', None)
    if contacts is None:
        return HttpResponseBadRequest()

    try:
        user.contacts = contacts
    except ValueError:
        return HttpResponseBadRequest()

    return HttpResponse()
