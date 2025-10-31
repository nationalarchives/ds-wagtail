import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition, Image
from wagtail.search import index

from app.core.serializers import RichTextSerializer


class TranscriptionHeadingChoices(models.TextChoices):
    TRANSCRIPT = "transcript", _("Transcript")
    PARTIAL_TRANSCRIPTION = "partial-transcript", _("Partial transcript")


class TranslationHeadingChoices(models.TextChoices):
    TRANSLATION = "translation", _("Translation")
    MODERN_ENGLISH = "modern-english", _("Modern English")


class CustomImage(AbstractImage):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="UUID",
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        help_text=_(
            "The descriptive name of the image. If this image features in a highlights gallery, this title will be visible on the page."
        ),
    )

    description = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_("alt text"),
        default="",
    )

    copyright = RichTextField(
        verbose_name=_("copyright"),
        blank=True,
        max_length=200,
        help_text=_(
            "Credit for images not owned by TNA. Do not include the copyright symbol."
        ),
        features=settings.INLINE_RICH_TEXT_FEATURES,
    )

    transcription_heading = models.CharField(
        verbose_name=_("transcript heading"),
        max_length=30,
        choices=TranscriptionHeadingChoices.choices,
        default=TranscriptionHeadingChoices.TRANSCRIPT,
    )

    transcription = RichTextField(
        verbose_name=_("transcript"),
        features=["bold", "italic", "ol", "ul"],
        blank=True,
        max_length=1500,
        help_text=_("If the image contains text consider adding a transcript."),
    )

    translation_heading = models.CharField(
        verbose_name=_("translation heading"),
        max_length=30,
        choices=TranslationHeadingChoices.choices,
        default=TranslationHeadingChoices.TRANSLATION,
        help_text=_(
            'If the original transcription language is some earlier form of English, choose "Modern English". If not, choose “Translation”.'
        ),
    )

    translation = RichTextField(
        verbose_name=_("translation"),
        features=["bold", "italic", "ol", "ul"],
        blank=True,
        max_length=1500,
        help_text=_(
            "An optional English / Modern English translation of the transcription."
        ),
    )

    search_fields = AbstractImage.search_fields + [
        index.SearchField("transcription", boost=1),
        index.SearchField("translation", boost=1),
        index.SearchField("copyright"),
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
        if hasattr(settings, "WAGTAILAPI_IMAGES_BASE_URL") and url.startswith("/"):
            return settings.WAGTAILAPI_IMAGES_BASE_URL + url
        return super().full_url()

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
