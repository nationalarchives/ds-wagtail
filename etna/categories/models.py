import os

from django.apps import apps
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet

# The path to where the static template tag will expect to find an image.
CATEGORIES_STATIC_PATH = "images/category-svgs/"
# The actual location of the image file within the system.
CATEGORIES_ICON_PATH = (
    apps.get_app_config("categories").path + "/static/" + CATEGORIES_STATIC_PATH
)


def icons_path():
    """
    Callable used as the 'path' value for `Category.icon` to avoid
    platform-specific icon paths in migrations.
    """
    return apps.get_app_config("categories").path + "/static/" + CATEGORIES_STATIC_PATH


@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=255)
    icon = models.FilePathField(path=icons_path, max_length=250, null=True, blank=True)

    panels = [FieldPanel("name"), FieldPanel("icon")]

    @property
    def icon_static_path(self):
        """icon_static_path

        The path to the icon required by the static template tag.
        """
        return f"{CATEGORIES_STATIC_PATH}{os.path.basename(self.icon)}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
