from django.urls import path

from . import views

urlpatterns = [
    path('questionnaire', views.questionnaire, name='questionnaire'),
    path('submission', views.submission, name='submission'),

    path('user/profile', views.profile, name='profile'),
    path('user/contacts', views.contacts, name='contacts'),
]
