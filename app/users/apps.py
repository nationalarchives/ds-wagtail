from django.apps import AppConfig
from wagtail.users.apps import WagtailUsersAppConfig


class UsersAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "app.users"
    verbose_name = "Users"
    default = True


class CustomUsersAppConfig(WagtailUsersAppConfig):
    user_viewset = "app.users.viewsets.UserViewSet"
