from django.db import models
from django.utils.text import slugify
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.coreutils import find_available_slug
from wagtail.fields import StreamField
from wagtail.search import index

from app.core.models import BasePageWithRequiredIntro

from .blocks import AnnexeStreamBlock, RequestStreamBlock, ResponseStreamBlock


class FoiIndexPage(BasePageWithRequiredIntro):
    class Meta:
        verbose_name = "Free of information listing page"

    max_count = 1
    subpage_types = ["foi.FoiRequestPage"]


class FoiRequestPage(BasePageWithRequiredIntro):
    class Meta:
        verbose_name = "Free of information request page"
        verbose_name_plural = "Free of information request pages"

    parent_page_types = ["foi.FoiIndexPage"]
    subpage_types = []

    reference = models.CharField(
        verbose_name="request reference",
        max_length=100,
        null=True,
    )

    date = models.DateTimeField(
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
    )

    content_panels = BasePageWithRequiredIntro.content_panels + [
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

    search_fields = BasePageWithRequiredIntro.search_fields + [
        index.SearchField("reference"),
        index.SearchField("request"),
        index.SearchField("outcome"),
        index.SearchField("response"),
        index.SearchField("annexe"),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
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
            self.slug = find_available_slug(self.get_parent(), slug)

        super().save(*args, **kwargs)
