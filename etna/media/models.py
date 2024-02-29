import mimetypes

from django.conf import settings
from django.db import models

from wagtail.api import APIField

from wagtailmedia.models import AbstractMedia

from etna.core.blocks.paragraph import RichTextField


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

    def mime(self):
        return mimetypes.guess_type(self.filename)[0] or "application/octet-stream"

    api_fields = [
        # APIField("file"),
        APIField("type"),
        # APIField("date"),
        APIField("url"),
        # APIField("sources"),
        APIField("mime"),
        # APIField("file_extension"),
        # APIField("thumbnail"),
        APIField("description"),
        APIField("transcript"),
    ]
