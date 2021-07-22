import os

from django.apps import apps
from django.db import models

from wagtail.snippets.models import register_snippet
from wagtail.admin.edit_handlers import FieldPanel


# The path to where the static template tag will expect to find an image.
CATEGORIES_STATIC_PATH = 'images/category-svgs/'
# The actual location of the image file within the system.
CATEGORIES_ICON_PATH = apps.get_app_config("categories").path + "/static/" + CATEGORIES_STATIC_PATH


@register_snippet
class Category(models.Model):

    name = models.CharField(max_length=255)
    icon = models.FilePathField(path=CATEGORIES_ICON_PATH, null=True, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("icon")
    ]

    def icon_static_path(self):
        """icon_static_path

        The path to the icon required by the static template tag.
        """
        return CATEGORIES_STATIC_PATH + os.path.basename(self.icon)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
