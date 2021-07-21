from django.apps import apps
from django.db import models

from wagtail.snippets.models import register_snippet
from wagtail.admin.edit_handlers import FieldPanel


CATEGORIES_ICON_PATH = apps.get_app_config("categories").path + "/static/images/category-svgs/"


@register_snippet
class Category(models.Model):

    name = models.CharField(max_length=255)
    icon = models.FilePathField(path=CATEGORIES_ICON_PATH, null=True, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("icon")
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
