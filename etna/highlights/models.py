from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.search import index

from etna.ciim.exceptions import KongAPIError
from etna.records.fields import RecordField


class Highlight(index.Indexed, models.Model):
    """
    Highlights are editable proxies of records that allow us to feature
    records in editorial content in a more controlled way, for example:

    - Overriding the record title and description to improve consistency.
    - Associating with a Wagtail image that can be used to generate thumbnails.
    - Adding data of interest like 'dates', that are not provided by CIIM.
    """

    record = RecordField(
        verbose_name=_("record"),
        help_text=_("The record (from CIIM) this highlight corresponds to."),
    )
    record.wagtail_reference_index_ignore = True

    title = models.CharField(
        verbose_name=_("title"),
        max_length=200,
        help_text=_(
            "A descriptive title to use when featuring this record in various places across the site (max length: 200 chars)."
        ),
    )
    dates = models.CharField(
        verbose_name=_("date(s)"),
        blank=True,
        max_length=100,
        help_text=_("Date(s) related to the record (max length: 100 chars)."),
    )
    description = RichTextField(
        verbose_name=_("description"),
        help_text=(
            "A 100-300 word description of the story of the record and why it is significant."
        ),
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
        max_length=900,
    )
    reference_number = models.CharField(
        verbose_name=_("reference number"),
        max_length=100,
        editable=False,
    )
    teaser_image = models.ForeignKey(
        get_image_model_string(),
        verbose_name=_("teaser image"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_(
            "Used to render a thumbnail image when featuring this highlight in various places across the site."
        ),
    )
    alt_text = models.CharField(
        verbose_name=_("image alt text"),
        max_length=100,
        help_text=mark_safe(
            'Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">Check the guidance for tips on writing alt text</a>.'
        ),
    )
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True)
    last_updated_at = models.DateTimeField(
        verbose_name=_("last updated at"), auto_now=True
    )

    search_fields = (
        index.AutocompleteField("title"),
        index.AutocompleteField("reference_number"),
        index.SearchField("title", boost=5),
        index.SearchField("reference_number", boost=2),
        index.SearchField("dates"),
        index.SearchField("description"),
        index.SearchField("alt_text"),
        index.FilterField("reference_number"),
        index.FilterField("teaser_image"),
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.reference_number})"

    def full_clean(self, *args, **kwargs) -> None:
        if not self.title:
            try:
                self.title = self.record.summary_title
            except (AttributeError, KongAPIError):
                pass

        if not self.reference_number:
            try:
                self.reference_number = self.record.reference_number
            except (AttributeError, KongAPIError):
                pass

        if not self.description:
            try:
                self.description = self.record.listing_description
            except (AttributeError, KongAPIError):
                pass
        super().full_clean(*args, **kwargs)
