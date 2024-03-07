import mimetypes

from django.conf import settings
from django.db import models

from wagtail.api import APIField
from wagtail.fields import RichTextField

from wagtailmedia.models import AbstractMedia

from etna.core.serializers import RichTextSerializer


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
        APIField("type"),
        APIField("url"),
        APIField("mime"),
        APIField("description", serializer=RichTextSerializer()),
        APIField("transcript", serializer=RichTextSerializer()),
    ]
