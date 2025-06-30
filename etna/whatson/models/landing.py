from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    InlinePanel,
    PageChooserPanel,
)
from wagtail.api import APIField

from etna.core.models import (
    BasePageWithRequiredIntro,
)

from ..serializers import (
    WhatsOnPageSelectionSerializer,
)


class WhatsOnPageSelection(models.Model):
    """
    This model is used to select a page to display on the What's On page.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="whats_on_page_selections",
    )

    featured_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("featured page"),
        help_text=_("The page to feature on the What's On page."),
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
        help_text=_("The page to display on the What's On page."),
    )

    panels = [
        PageChooserPanel(
            "featured_page",
            page_type=[
                "whatson.EventPage",
                "whatson.ExhibitionPage",
                "whatson.DisplayPage",
            ],
        ),
        PageChooserPanel(
            "selected_page",
            page_type=[
                "whatson.ExhibitionsListingPage",
                "whatson.EventsListingPage",
                "whatson.WhatsOnSeriesPage",
                "whatson.WhatsOnCategoryPage",
            ],
        ),
    ]

    class Meta:
        verbose_name = _("selection")


class WhatsOnPage(BasePageWithRequiredIntro):
    """
    A page for listing events.
    """

    @cached_property
    def type_label(cls) -> str:
        return "What's On"

    class Meta:
        verbose_name = _("What's On page")

    parent_page_types = [
        "home.HomePage",
    ]
    subpage_types = [
        "whatson.EventsListingPage",
        "whatson.ExhibitionsListingPage",
        "whatson.WhatsOnSeriesPage",
        "whatson.WhatsOnCategoryPage",
        "whatson.WhatsOnLocationListingPage",
        "whatson.WhatsOnDateListingPage",
    ]

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
        InlinePanel(
            "whats_on_page_selections",
            heading=_("Page selections"),
            help_text=_("Select pages to display on the What's On page."),
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField(
            "whats_on_page_selections",
            serializer=WhatsOnPageSelectionSerializer(many=True),
        ),
    ]
