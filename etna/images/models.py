from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition
from wagtail.search import index

from etna.ciim.fields import RecordField
from etna.ciim.serializers import RecordSerializer
from etna.core.serializers import RichTextSerializer

DEFAULT_SENSITIVE_IMAGE_WARNING = (
    "This image contains content which some people may find offensive or distressing."
)


class TranscriptionHeadingChoices(models.TextChoices):
    TRANSCRIPT = "transcript", _("Transcript")
    PARTIAL_TRANSCRIPTION = "partial-transcript", _("Partial transcript")


class TranslationHeadingChoices(models.TextChoices):
    TRANSLATION = "translation", _("Translation")
    MODERN_ENGLISH = "modern-english", _("Modern English")


class CustomImage(ClusterableModel, AbstractImage):
    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        help_text=_(
            "The descriptive name of the image. If this image features in a highlights gallery, this title will be visible on the page."
        ),
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

    is_sensitive = models.BooleanField(
        verbose_name=_("This image is considered sensitive"),
        default=False,
        help_text=_(
            "Tick this if the image contains content which some people may find offensive or distressing. For example, photographs of violence or injury detail."
        ),
    )

    custom_sensitive_image_warning = models.CharField(
        verbose_name=_("Why might this image be considered sensitive? (optional)"),
        help_text=_(
            'Replaces the default warning message where the image is displayed. For example: "This image has been marked as potentially sensitive because it contains depictions of violence".'
        ),
        max_length=200,
        blank=True,
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

    # For Highlights

    record = RecordField(
        verbose_name=_("related record"),
        db_index=True,
        blank=True,
        help_text=_(
            "If the image relates to a specific record, select that record here."
        ),
    )
    record.wagtail_reference_index_ignore = True

    record_dates = models.CharField(
        verbose_name=_("record date(s)"),
        max_length=100,
        blank=True,
        help_text=_("Date(s) related to the selected record (max length: 100 chars)."),
    )

    description = RichTextField(
        verbose_name=_("description"),
        help_text=(
            "This text will appear in highlights galleries. A 100-300 word "
            "description of the story of the record and why it is significant."
        ),
        blank=True,
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
        max_length=900,
    )

    search_fields = AbstractImage.search_fields + [
        index.SearchField("transcription", boost=1),
        index.SearchField("translation", boost=1),
        index.SearchField("description"),
        index.SearchField("copyright"),
        index.FilterField("record"),
        index.FilterField("is_sensitive"),
    ]

    api_fields = [
        APIField("title"),
        APIField("copyright"),
        APIField("description", serializer=RichTextSerializer()),
        APIField("transcription_heading"),
        APIField("transcription", serializer=RichTextSerializer()),
        APIField("translation_heading"),
        APIField("translation", serializer=RichTextSerializer()),
        APIField("record_dates"),
        APIField("record", serializer=RecordSerializer()),
    ]

    @property
    def sensitive_image_warning(self):
        return (
            self.custom_sensitive_image_warning.strip()
            or DEFAULT_SENSITIVE_IMAGE_WARNING
        )

    admin_form_fields = [
        "collection",
        "title",
        "file",
        "copyright",
        "is_sensitive",
        "custom_sensitive_image_warning",
        "tags",
        "focal_point_x",
        "focal_point_y",
        "focal_point_width",
        "focal_point_height",
        "transcription_heading",
        "transcription",
        "translation_heading",
        "translation",
        "record",
        "record_dates",
        "description",
    ]


class CustomImageRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    @property
    def full_url(self):
        url = self.url
        if url.startswith("/"):
            if (
                hasattr(settings, "WAGTAILAPI_IMAGES_BASE_URL")
                and settings.WAGTAILAPI_IMAGES_BASE_URL
            ):
                url = settings.WAGTAILAPI_IMAGES_BASE_URL + url
            elif hasattr(settings, "WAGTAILADMIN_BASE_URL"):
                url = settings.WAGTAILADMIN_BASE_URL + url
        return url

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
