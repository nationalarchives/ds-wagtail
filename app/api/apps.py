from django.apps import AppConfig


class ApiAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "app.api"
    verbose_name = "API"

    def ready(self):
        from app.api.v3.schemas import register_page_schemas

        register_page_schemas()
