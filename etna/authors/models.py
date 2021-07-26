from django.conf import settings
from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Author(models.Model):
    """Author snippet

    Model to store author details. Including image and a link to
    an external biography page.
    """
    name = models.CharField(blank=False, null=False, max_length=100)
    role = models.CharField(blank=True, null=True, max_length=100)
    summary = RichTextField(blank=True, null=True, features=settings.INLINE_RICH_TEXT_FEATURES)
    image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    bio_link = models.URLField(blank=False, null=False, help_text="Link to external bio page")
    bio_link_label = models.CharField(blank=False, null=False, help_text="Button text for bio link", max_length=50)

    panels = [
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("summary"),
        ImageChooserPanel("image"),
        FieldPanel("bio_link"),
        FieldPanel("bio_link_label"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Authors"
