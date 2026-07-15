import mimetypes
import uuid

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from wagtail import blocks
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.rich_text import expand_db_html
from wagtailmedia.models import AbstractMedia
from wagtailmedia.settings import wagtailmedia_settings

from app.core.blocks.paragraph import APIRichTextBlock
from app.core.serializers import RichTextSerializer
from app.media.blocks import ChapterTimeBlock
from app.media.time_utils import parse_chapter_time_to_seconds


class MediaChapterSectionBlock(blocks.StructBlock):
    time = ChapterTimeBlock(
        required=True,
        default="00:00:00",
        label="Chapter time",
        help_text="Enter chapter time as HH:MM:SS.",
    )
    heading = blocks.CharBlock(max_length=20)
    transcript = APIRichTextBlock(required=False, features=["bold", "italic"])

    class Meta:
        label = "Chapter"


class AlternateVersionTypes(models.TextChoices):
    AUDIO_DESCRIBED = "audio_described", "Audio Described"
    SUBTITLED = "subtitled", "Subtitled"


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
    alternate_version_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="alternate version link",
        help_text="Link to an alternate version of the media.",
    )
    alternate_version_type = models.CharField(
        max_length=20,
        verbose_name="alternate version type",
        help_text="The type of the alternate version.",
        choices=AlternateVersionTypes.choices,
        blank=True,
        null=True,
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

        if self.audio_described_file:
            # Validate audio_described_file based on media type
            if self.type == "audio" and wagtailmedia_settings.AUDIO_EXTENSIONS:
                validate = FileExtensionValidator(
                    wagtailmedia_settings.AUDIO_EXTENSIONS
                )
                validate(self.audio_described_file)
            elif self.type == "video" and wagtailmedia_settings.VIDEO_EXTENSIONS:
                validate = FileExtensionValidator(
                    wagtailmedia_settings.VIDEO_EXTENSIONS
                )
                validate(self.audio_described_file)

        if self.subtitles_file:
            validate = FileExtensionValidator(["vtt"])
            validate(self.subtitles_file)
        if self.chapters_file:
            validate = FileExtensionValidator(["vtt"])
            validate(self.chapters_file)

    @property
    def full_url(self):
        url = self.url
        if url.startswith("/"):
            if (
                hasattr(settings, "WAGTAILAPI_MEDIA_BASE_URL")
                and settings.WAGTAILAPI_MEDIA_BASE_URL
            ):
                url = settings.WAGTAILAPI_MEDIA_BASE_URL + url
            elif hasattr(settings, "WAGTAILADMIN_BASE_URL"):
                url = settings.WAGTAILADMIN_BASE_URL + url
        return url

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
        "alternate_version_link",
        "alternate_version_type",
        "chapters",
        "collection",
        "description",
        "duration",
        "transcript",
        "subtitles_file",
        "chapters_file",
        "tags",
    )

    def mime(self):
        return mimetypes.guess_type(self.filename)[0] or "application/octet-stream"

    def api_chapters(self):
        chapter_pairs = []
        for chapter in self.chapters:
            value = chapter.value
            sort_key = parse_chapter_time_to_seconds(value["time"])
            chapter_pairs.append(
                (
                    sort_key,
                    {
                        "time": sort_key,
                        "heading": value["heading"],
                        "transcript": expand_db_html(value["transcript"].source),
                    },
                )
            )

        return [
            chapter_payload
            for _, chapter_payload in sorted(chapter_pairs, key=lambda pair: pair[0])
        ]

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
