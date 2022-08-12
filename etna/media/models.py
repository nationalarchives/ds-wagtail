from django.conf import settings
from django.db import models

from wagtail.fields import RichTextField

from wagtailmedia.models import AbstractMedia


class EtnaMedia(AbstractMedia):
    """
    Extend wagtailmedia model.
    """

    date = models.DateField(blank=True, null=True)
    description = RichTextField(
        blank=True, null=True, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    transcript = RichTextField(
        blank=True, null=True, features=settings.INLINE_RICH_TEXT_FEATURES
    )

    admin_form_fields = (
        "title",
        "date",
        "file",
        "collection",
        "description",
        "duration",
        "width",
        "height",
        "thumbnail",
        "transcript",
        "tags",
    )
