import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
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


class AlternativeFormatHeadingChoices(models.TextChoices):
    TRANSCRIPT_WITH_TABLES = "transcript-with-tables", "Transcript with tables"


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

    alternative_format_heading = models.CharField(
        verbose_name="alternative format heading",
        max_length=30,
        choices=AlternativeFormatHeadingChoices.choices,
        blank=True,
        help_text="If the image has an alternative format, choose the appropriate heading.",
    )

    alternative_format = models.FileField(
        verbose_name="alternative format",
        blank=True,
        null=True,
        upload_to="images/alternative_formats/",
        help_text="An optional alternative format of the image, e.g. a spreadsheet.",
        validators=[FileExtensionValidator(["csv", "xlsx", "xls"])],
    )

    def usage_count(self):
        return self.get_usage().count()

    @property
    def original_width(self):
        return self.file.width

    @property
    def original_height(self):
        return self.file.height

    @property
    def original_file_size(self):
        return self.file.size

    def clean(self):
        super().clean()

        if self.alternative_format and not self.alternative_format_heading:
            raise ValidationError(
                {
                    "alternative_format_heading": "Choose an alternative format heading when an alternative format file is uploaded.",
                }
            )

        if self.alternative_format_heading and not self.alternative_format:
            raise ValidationError(
                {
                    "alternative_format": "Upload an alternative format file when an alternative format heading is selected.",
                }
            )

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
        APIField("alternative_format_heading"),
        APIField("alternative_format"),
        APIField("original_width"),
        APIField("original_height"),
        APIField("original_file_size"),
    ]

    admin_form_fields = Image.admin_form_fields + (
        "copyright",
        "transcription_heading",
        "transcription",
        "translation_heading",
        "translation",
        "alternative_format_heading",
        "alternative_format",
    )


class CustomImageRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
