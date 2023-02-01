from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.models import ClusterableModel
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition, Image

from etna.records.fields import RecordField


class CustomImage(ClusterableModel, AbstractImage):
    record = RecordField(
        verbose_name=_("related record"),
        db_index=True,
        blank=True,
        help_text=_(
            "If the image relates to a specific record, select that record here."
        ),
    )
    record_dates = models.CharField(
        verbose_name=_("record date(s)"),
        max_length=100,
        blank=True,
        help_text=_("Date(s) related to the selected record (max length: 100 chars)."),
    )

    description = RichTextField(
        verbose_name=_("description"),
        blank=True,
        features=settings.INLINE_RICH_TEXT_FEATURES,
        max_length=500,
    )

    transcription = RichTextField(
        verbose_name=_("transcription"),
        features=["bold", "italic", "ol", "ul"],
        max_length=1500,
        help_text=_("An optional transcription of the image."),
        blank=True,
    )
    transcription_language = models.CharField(
        verbose_name=_("transcription language"),
        blank=True,
        help_text="For example: Old English.",
        max_length=50,
    )

    admin_form_fields = Image.admin_form_fields + (
        "record",
        "record_dates",
        "description",
        "transcription",
        "transcription_language",
    )


class CustomImageRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)
