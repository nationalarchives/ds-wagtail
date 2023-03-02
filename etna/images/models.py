from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.models import ClusterableModel
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition
from wagtail.search import index

from etna.records.fields import RecordField


class TranscriptionHeadingChoices(models.TextChoices):
    DEFAULT = "default", _("Transcription")
    PARTIAL_TRANSCRIPTION = "partial-transcription", _("Partial transcription")


class TranslationHeadingChoices(models.TextChoices):
    DEFAULT = "default", _("Translation")
    MODERN_ENGLISH = "modern-english", _("Modern English")


class CustomImage(ClusterableModel, AbstractImage):
    copyright = models.CharField(
        verbose_name=_("Copyright"), blank=True, max_length=120, help_text="???"
    )

    is_sensitive = models.BooleanField(
        verbose_name=_("This image is sensitive"), default=False
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
        help_text="??",
        blank=True,
        features=settings.INLINE_RICH_TEXT_FEATURES,
        max_length=900,
    )

    transcription_heading = models.CharField(
        max_length=30,
        choices=TranscriptionHeadingChoices.choices,
        default=TranscriptionHeadingChoices.DEFAULT,
        help_text="???",
    )

    transcription = RichTextField(
        verbose_name=_("transcription"),
        features=["bold", "italic", "ol", "ul"],
        max_length=1500,
        help_text=_("An optional transcription of the image."),
        blank=True,
    )

    translation_heading = models.CharField(
        max_length=30,
        choices=TranslationHeadingChoices.choices,
        default=TranslationHeadingChoices.DEFAULT,
        help_text="???",
    )

    translation = RichTextField(
        verbose_name=_("translation"),
        features=["bold", "italic", "ol", "ul"],
        max_length=1500,
        help_text=_(
            "An optional English / Modern English translation of the transcription."
        ),
        blank=True,
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
