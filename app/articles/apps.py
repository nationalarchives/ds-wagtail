from django.apps import AppConfig


class ArticleAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "app.articles"
    verbose_name = "Articles"
