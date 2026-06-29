import uuid

from django.conf import settings
from django.db import models
from modelcluster.models import ClusterableModel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.search import index

from app.core.serializers import RichTextSerializer


class TranscriptionHeadingChoices(models.TextChoices):
    TRANSCRIPT = "transcript", "Transcript"
    PARTIAL_TRANSCRIPTION = "partial-transcript", "Partial transcript"


class TranslationHeadingChoices(models.TextChoices):
    TRANSLATION = "translation", "Translation"
    MODERN_ENGLISH = "modern-english", "Modern English"


class CustomImage(ClusterableModel, AbstractImage):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="UUID",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="title",
        help_text="The descriptive name of the image. If this image features in a highlights gallery, this title will be visible on the page.",
    )

    description = models.CharField(
        blank=True,
        max_length=255,
        verbose_name="alt text",
        default="",
    )

    copyright = RichTextField(
        verbose_name="copyright",
        blank=True,
        max_length=200,
        help_text="Credit for images not owned by TNA. Do not include the copyright symbol.",
        features=settings.INLINE_RICH_TEXT_FEATURES,
    )

    transcription_heading = models.CharField(
        verbose_name="transcript heading",
        max_length=30,
        choices=TranscriptionHeadingChoices.choices,
        default=TranscriptionHeadingChoices.TRANSCRIPT,
    )

    transcription = RichTextField(
        verbose_name="transcript",
        features=["bold", "italic", "ol", "ul"],
        blank=True,
        max_length=4500,
        help_text="If the image contains text consider adding a transcript.",
    )

    translation_heading = models.CharField(
        verbose_name="translation heading",
        max_length=30,
        choices=TranslationHeadingChoices.choices,
        default=TranslationHeadingChoices.TRANSLATION,
        help_text='If the original transcription language is some earlier form of English, choose "Modern English". If not, choose “Translation”.',
    )

    translation = RichTextField(
        verbose_name="translation",
        features=["bold", "italic", "ol", "ul"],
        blank=True,
        max_length=4500,
        help_text="An optional English / Modern English translation of the transcription.",
    )

    def usage_count(self):
        return self.get_usage().count()

    search_fields = AbstractImage.search_fields + [
        index.SearchField("transcription", boost=1),
        index.SearchField("translation", boost=1),
        index.SearchField("copyright"),
        index.FilterField("usage_count"),
    ]

    api_fields = [
        APIField("uuid"),
        APIField("title"),
        APIField("copyright"),
        APIField("description"),
        APIField("transcription_heading"),
        APIField("transcription", serializer=RichTextSerializer()),
        APIField("translation_heading"),
        APIField("translation", serializer=RichTextSerializer()),
    ]

    admin_form_fields = Image.admin_form_fields + (
        "copyright",
        "transcription_heading",
        "transcription",
        "translation_heading",
        "translation",
    )


class CustomImageRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    @property
    def full_url(self):
        url = self.url
        if hasattr(settings, "WAGTAILAPI_MEDIA_BASE_URL") and url.startswith("/"):
            return settings.WAGTAILAPI_MEDIA_BASE_URL + url
        return super().full_url()

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
