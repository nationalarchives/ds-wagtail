from django.db import models
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
        "Responded": {
            100: "Information provided",
            101: "Some information provided",
            102: "Information not held",
            103: "Information withheld",
        },
        "Refused": {
            200: "Request refused",
            201: "Request refused - under the cost limit",
        },
    }
    outcome = models.IntegerField(
        choices=REQUEST_OUTCOMES,
    )

    response = StreamField(
        ResponseStreamBlock,
        null=True,
    )

    annexe = StreamField(
        AnnexeStreamBlock,
        null=True,
        blank=True,
    )

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

    search_fields = BasePage.search_fields + [
        index.SearchField("reference"),
        index.SearchField("request"),
        index.SearchField("outcome"),
        index.SearchField("response"),
        index.SearchField("annexe"),
    ]

    api_fields = BasePage.api_fields + [
        APIField("reference"),
        APIField("date"),
        APIField("request"),
        APIField("outcome"),
        APIField("response"),
        APIField("annexe"),
    ]

    def save(self, *args, **kwargs):
        if self.reference:
            slug = slugify(self.reference)
            if slug not in self.slug:
                self.slug = find_available_slug(self.get_parent(), slug)

            if not self.short_title:
                new_short_title = f"FOI request {self.reference}"
                short_title_max_length = self._meta.get_field("short_title").max_length
                if len(new_short_title) <= short_title_max_length:
                    self.short_title = new_short_title
                else:
                    self.short_title = (
                        f"{new_short_title[:short_title_max_length - 3]}..."
                    )

        super().save(*args, **kwargs)
