from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.models import ClusterableModel
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition
from wagtail.search import index

from etna.records.fields import RecordField


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

    copyright = models.CharField(
        verbose_name=_("copyright"),
        blank=True,
        max_length=120,
        help_text=_(
            "Credit for images not owned by TNA. Do not include the copyright symbol."
        ),
    )

    is_sensitive = models.BooleanField(
        verbose_name=_("This image is sensitive"), default=False
    )

    transcription_heading = models.CharField(
        verbose_name=_("transcription heading"),
        max_length=30,
        choices=TranscriptionHeadingChoices.choices,
        default=TranscriptionHeadingChoices.TRANSCRIPT,
    )

    transcription = RichTextField(
        verbose_name=_("transcription"),
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

    search_fields = [
        index.SearchField("transcription", boost=1),
        index.SearchField("translation", boost=1),
        index.SearchField("description"),
        index.SearchField("copyright"),
        index.FilterField("record"),
        index.FilterField("is_sensitive"),
    ]

    admin_form_fields = [
        "collection",
        "title",
        "file",
        "copyright",
        "is_sensitive",
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

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
