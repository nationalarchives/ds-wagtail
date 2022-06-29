from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login, name="account_login"),
    path("logout/", views.logout, name="account_logout"),
    path("register/", views.register, name="account_register"),
    path("authorize/", views.authorize, name="account_authorize"),
]
