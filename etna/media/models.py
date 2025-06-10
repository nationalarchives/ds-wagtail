import mimetypes
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from wagtail import blocks
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtailmedia.models import AbstractMedia

from etna.core.blocks.paragraph import APIRichTextBlock
from etna.core.serializers import RichTextSerializer


class MediaChapterSectionBlock(blocks.StructBlock):
    time = blocks.IntegerBlock(
        blank=True,
        default=0,
        validators=[MinValueValidator(0)],
        label="Time in seconds",
    )
    heading = blocks.CharBlock(max_length=20)
    transcript = APIRichTextBlock(required=False, features=["bold", "italic"])

    class Meta:
        label = "Chapter"


class EtnaMedia(AbstractMedia):
    """
    Extend wagtailmedia model.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="UUID",
    )
    audio_described_file = models.FileField(
        blank=True,
        null=True,
        upload_to="media",
        verbose_name="audio described file",
    )
    date = models.DateField(blank=True, null=True)
    description = RichTextField(
        blank=True, null=True, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    transcript = RichTextField(
        blank=True, null=True, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    subtitles_file = models.FileField(
        blank=True, null=True, upload_to="media", verbose_name="subtitles file"
    )
    chapters_file = models.FileField(
        blank=True, null=True, upload_to="media", verbose_name="chapters file"
    )

    chapters = StreamField(
        [
            ("chapter", MediaChapterSectionBlock()),
        ],
        blank=True,
        null=True,
    )

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        if self.subtitles_file:
            validate = FileExtensionValidator(["vtt"])
            validate(self.subtitles_file)
        if self.chapters_file:
            validate = FileExtensionValidator(["vtt"])
            validate(self.chapters_file)

    # Added full_url to be sent to the frontend via the Wagtail API
    @property
    def full_url(self):
        return settings.WAGTAILADMIN_BASE_URL + self.file.url

    @property
    def subtitles_file_url(self):
        if self.subtitles_file and hasattr(self.subtitles_file, "url"):
            return self.subtitles_file.url

    @property
    def subtitles_file_full_url(self):
        if self.subtitles_file and hasattr(self.subtitles_file, "url"):
            return settings.WAGTAILADMIN_BASE_URL + self.subtitles_file.url

    @property
    def chapters_file_url(self):
        if self.chapters_file and hasattr(self.chapters_file, "url"):
            return self.chapters_file.url

    @property
    def chapters_file_full_url(self):
        if self.chapters_file and hasattr(self.chapters_file, "url"):
            return settings.WAGTAILADMIN_BASE_URL + self.chapters_file.url

    admin_form_fields = (
        "title",
        "date",
        "file",
        "audio_described_file",
        "chapters",
        "collection",
        "description",
        "duration",
        "width",
        "height",
        "thumbnail",
        "transcript",
        "subtitles_file",
        "chapters_file",
        "tags",
    )

    def mime(self):
        return mimetypes.guess_type(self.filename)[0] or "application/octet-stream"

    api_fields = [
        APIField("type"),
        APIField("url"),
        APIField("mime"),
        APIField("chapters"),
        APIField("description", serializer=RichTextSerializer()),
        APIField("transcript", serializer=RichTextSerializer()),
        APIField("subtitles_file"),
        APIField("chapters_file"),
    ]
