from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "app.blog"
    verbose_name = "Blog"
