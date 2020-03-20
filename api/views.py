from http import HTTPStatus

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods, require_GET

from .models import Questionnaire, Submission


class HttpResponseNoContent(HttpResponse):
    status_code = HTTPStatus.NO_CONTENT


@require_GET
def questionnaire(request):
    q = Questionnaire.objects.order_by('-date_created').first()
    return JsonResponse({'questionnaire': q.content})


@require_http_methods(["GET", "POST"])
def submission(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    user = request.user

    if request.method == "GET":
        s = Submission.objects.filter(user=user).order_by('-submission_time').first()
        content = s.content if s is not None else None
        return JsonResponse({'submission': content})

    data = request.POST.get('data', None)
    if data is None:
        return HttpResponseBadRequest()

    q = Questionnaire.objects.order_by('-date_created').first()
    submission = Submission(questionnaire=q, user=user, content=data)
    submission.save()
    return HttpResponseNoContent()


@require_http_methods(["GET", "POST"])
def profile(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    user = request.user

    if request.method == "GET":
        return JsonResponse(user.profile)

    data = request.POST.get('data', None)
    if data is None:
        return HttpResponseBadRequest()

    try:
        user.profile = data
    except ValueError:
        return HttpResponseBadRequest()

    return HttpResponseNoContent()


@require_http_methods(["GET", "POST"])
def contacts(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    user = request.user

    if request.method == "GET":
        return JsonResponse({'contacts': user.contacts})

    contacts = request.POST.get('contacts', None)
    if contacts is None:
        return HttpResponseBadRequest()

    try:
        user.contacts = contacts
    except ValueError:
        return HttpResponseBadRequest()

    return HttpResponseNoContent()
