from django.db import models
from django.conf import settings

from wagtail.snippets.models import register_snippet
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=255)
    icon = models.FilePathField(path=settings.CATEGORIES_ICON_PATH, null=True, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("icon")
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
