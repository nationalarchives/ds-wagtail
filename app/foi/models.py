from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.coreutils import find_available_slug
from wagtail.fields import StreamField
from wagtail.search import index

from app.core.models import BasePage, BasePageWithRequiredIntro

from .blocks import AnnexeStreamBlock, RequestStreamBlock, ResponseStreamBlock


class FoiIndexPage(BasePageWithRequiredIntro):
    class Meta:
        verbose_name = "Freedom of information listing page"

    max_count = 1
    subpage_types = ["foi.FoiRequestPage"]


class FoiRequestPage(BasePage):
    class Meta:
        verbose_name = "Freedom of information request page"
        verbose_name_plural = "Freedom of information request pages"

    parent_page_types = ["foi.FoiIndexPage"]
    subpage_types = []

    # Not a required field like in BasePage
    teaser_text = models.TextField(
        max_length=160,
        null=True,
        blank=True,
    )

    reference = models.CharField(
        verbose_name="request reference",
        max_length=100,
        null=True,
    )

    date = models.DateField(
        verbose_name="publication date",
        help_text="The date the request was published.",
        null=True,
    )

    request = StreamField(
        RequestStreamBlock,
        null=True,
    )

    REQUEST_OUTCOMES = {
        "P": "Information provided",
        "S": "Some information provided",
        "N": "Information not held",
        "W": "Information withheld",
        "R": "Request refused",
    }
    outcome = models.CharField(
        max_length=1,
        choices=REQUEST_OUTCOMES,
    )

    @cached_property
    def outcome_description(self):
        return self.REQUEST_OUTCOMES.get(self.outcome, "")

    response = StreamField(
        ResponseStreamBlock,
        null=True,
    )

    annexe = StreamField(
        AnnexeStreamBlock,
        null=True,
        blank=True,
    )

    @cached_property
    def type_label(cls) -> str:
        return "Freedom of information request"

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            heading="Request",
            classname="collapsible",
            children=[
                FieldPanel("reference"),
                FieldPanel("date"),
                FieldPanel("request"),
            ],
        ),
        FieldPanel("outcome"),
        FieldPanel("response"),
        FieldPanel("annexe"),
    ]

    # Remove certain promote panels from BasePage as these will be auto-generated
    promote_panels = [
        panel
        for panel in BasePage.promote_panels
        if not (
            (hasattr(panel, "heading") and panel.heading == "Internal data")
            or (hasattr(panel, "heading") and panel.heading == "For search engines")
            or (hasattr(panel, "field_name") and panel.field_name == "short_title")
        )
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("reference"),
        index.SearchField("request"),
        index.SearchField("outcome_description"),
        index.SearchField("response"),
        index.SearchField("annexe"),
    ]

    api_fields = BasePage.api_fields + [
        APIField("reference"),
        APIField("date"),
        APIField("request"),
        APIField("outcome_description"),
        APIField("response"),
        APIField("annexe"),
    ]

    def save(self, *args, **kwargs):
        if self.reference:
            slug = slugify(self.reference)
            if slug not in self.slug:
                self.slug = find_available_slug(self.get_parent(), slug)

            new_short_title = f"FOI request: {self.reference}"
            short_title_max_length = self._meta.get_field("short_title").max_length
            if len(new_short_title) <= short_title_max_length:
                self.short_title = new_short_title
            else:
                self.short_title = f"{new_short_title[:short_title_max_length - 3]}..."

            new_teaser_text = f'Freedom of information request: "{self.title}"'
            teaser_text_max_length = self._meta.get_field("teaser_text").max_length
            if len(new_teaser_text) <= teaser_text_max_length:
                self.teaser_text = new_teaser_text
            else:
                self.teaser_text = f'{new_teaser_text[:teaser_text_max_length - 4]}..."'

        if self.date:
            # Change the date to the first of the month
            self.date = self.date.replace(day=1)

        return super().save(*args, **kwargs)
