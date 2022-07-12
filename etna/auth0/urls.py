from django.urls import path

from . import views

"""
NOTE: The intention here is to mimic allauth in terms of naming / paths, so
that you can always use django.urls.reverse() or {% url 'url_name' %} tag to
link to the key views, regardless of whether AUTH0 is configured/enabled.
"""
urlpatterns = [
    path("login/", views.login, name="account_login"),
    path("logout/", views.logout, name="account_logout"),
    path("signup/", views.register, name="account_signup"),
    path("authorize/", views.authorize, name="account_authorize"),
]
