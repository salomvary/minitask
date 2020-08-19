from django.contrib.auth import views as auth_views
from django.urls import path

from . import forms

urlpatterns = [
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(authentication_form=forms.AuthenticationForm),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
