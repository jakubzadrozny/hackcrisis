from django.contrib import admin

from .models import Questionnaire, Submission


admin.site.register(Questionnaire)
admin.site.register(Submission)
