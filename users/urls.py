from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('request_token', views.request_token, name='request_token'),
    path('login', views.login_view, name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
]
