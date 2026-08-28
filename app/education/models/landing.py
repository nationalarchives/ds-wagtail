from django.db import models
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.models import Orderable

from app.core.models import (
    BasePageWithRequiredIntro,
    RequiredHeroImageMixin,
)
from app.core.serializers import DefaultPageSerializer

from ..serializers import LinkedPageSerializer
from .listings import EducationSessionsListingPage, TeachingResourcesListingPage


class EducationPage(RequiredHeroImageMixin, BasePageWithRequiredIntro):
    """
    A page for listing teaching resources and sessions.
    """

    @cached_property
    def teaching_resources_listing(self):
        return (
            self.get_children()
            .type(TeachingResourcesListingPage)
            .live()
            .public()
            .first()
        )

    @cached_property
    def education_sessions_listing(self):
        return (
            self.get_children()
            .type(EducationSessionsListingPage)
            .live()
            .public()
            .first()
        )

    parent_page_types = [
        "home.HomePage",
    ]

    subpage_types = [
        "education.EducationSessionsListingPage",
        "education.TeachingResourcesListingPage",
        "generic_pages.GeneralPage",
        "generic_pages.HubPage",
    ]

    max_count = 1

    # Teaching resources section
    teaching_resources_listing_page = models.ForeignKey(
        "education.TeachingResourcesListingPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="teaching resource listing page",
        help_text="The teaching resource listing page to display on the Education landing page.",
    )

    teaching_resources_teaser_override = models.CharField(
        verbose_name="teaching resources teaser text",
        help_text="Short text under Explore teaching resources title to entice users to click through",
        blank=True,
        max_length=160,
    )

    # Education sessions section
    education_sessions_listing_page = models.ForeignKey(
        "education.EducationSessionsListingPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="education sessions listing page",
        help_text="The education sessions listing page to display on the Education landing page.",
    )

    education_sessions_teaser_override = models.CharField(
        verbose_name="education sessions teaser text",
        help_text="Short text under Explore education sessions title to entice users to click through",
        blank=True,
        max_length=160,
    )

    featured_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="featured education page",
        help_text="Page picker to highlight a featured education page (session, resource, or hub/general)",
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            InlinePanel(
                "education_read_more_links",
                heading="Read more",
                help_text="Navigation to other sections within Education",
            ),
            MultiFieldPanel(
                [
                    PageChooserPanel(
                        "featured_page",
                        [
                            "education.EducationSessionPage",
                            "education.TeachingResourcePage",
                            "generic_pages.GeneralPage",
                            "generic_pages.HubPage",
                        ],
                    ),
                ],
                heading="Featured page",
            ),
        ]
    )

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + [
            APIField("teaching_resources_listing", serializer=DefaultPageSerializer()),
            APIField("teaching_resources_teaser_override"),
            APIField("education_sessions_listing", serializer=DefaultPageSerializer()),
            APIField("education_sessions_teaser_override"),
            APIField(
                "featured_page",
                serializer=DefaultPageSerializer(
                    required_api_fields=["session_locations", "start_date", "end_date"]
                ),
            ),
            APIField(
                "education_read_more_links",
                serializer=LinkedPageSerializer(many=True),
            ),
        ]
    )

    class Meta:
        verbose_name = "Education landing page"


class EducationReadMoreLink(Orderable):
    """Navigation links for the Read more section"""

    page = ParentalKey(
        "education.EducationPage",
        on_delete=models.CASCADE,
        related_name="education_read_more_links",
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="selected page",
    )

    panels = [
        PageChooserPanel(
            "selected_page",
            [
                "education.EducationSessionPage",
                "education.TeachingResourcePage",
                "generic_pages.GeneralPage",
                "generic_pages.HubPage",
            ],
        ),
    ]

    class Meta:
        verbose_name = "read more link"
        ordering = ["sort_order"]
