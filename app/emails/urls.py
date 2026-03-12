from django.urls import path

from . import views

app_name = "email"
urlpatterns = [path("", views.email, name="email")]
