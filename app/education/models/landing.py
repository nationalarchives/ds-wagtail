from django.db import models
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.models import Orderable

from app.core.models import (
    BasePageWithRequiredIntro,
)
from app.core.serializers import DefaultPageSerializer

from ..serializers import LinkedPageSerializer
from .listings import EducationSessionsListingPage, TeachingResourcesListingPage
from .resources import TeachingResourcePage
from .sessions import EducationSessionPage


class EducationPage(BasePageWithRequiredIntro):
    """
    A page for listing teaching resources and sessions.
    """

    @cached_property
    def type_label(self) -> str:
        return "Education"

    @cached_property
    def latest_teaching_resources(self) -> list:
        return list(
            TeachingResourcePage.objects.live().public().order_by("-published_date")[:3]
        )

    @cached_property
    def latest_education_sessions(self) -> list:
        return list(
            EducationSessionPage.objects.live().public().order_by("-start_date")[:3]
        )

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

    featured_teaching_resource = models.ForeignKey(
        "education.TeachingResourcePage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="featured teaching resource",
        help_text="Option to add a highlighted teaching resource, particularly for history months etc",
    )

    featured_teaching_resource_teaser_override = models.CharField(
        verbose_name="Featured teaching resource teaser text override",
        help_text="Override text for the featured teaching resource",
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

    featured_education_session = models.ForeignKey(
        "education.EducationSessionPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="featured education session",
        help_text="Page picker to highlight a featured education session",
    )

    featured_education_session_teaser_override = models.CharField(
        verbose_name="Featured education session teaser text override",
        help_text="Override text for the featured education session",
        blank=True,
        max_length=160,
    )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("teaching_resources_teaser_override"),
                MultiFieldPanel(
                    [
                        PageChooserPanel("featured_teaching_resource"),
                        FieldPanel("featured_teaching_resource_teaser_override"),
                    ],
                ),
            ],
            heading="Teaching resources",
        ),
        MultiFieldPanel(
            [
                FieldPanel("education_sessions_teaser_override"),
                MultiFieldPanel(
                    [
                        PageChooserPanel("featured_education_session"),
                        FieldPanel("featured_education_session_teaser_override"),
                    ],
                ),
            ],
            heading="Education sessions",
        ),
        InlinePanel(
            "education_read_more_links",
            heading="Read more",
            help_text="Navigation to other sections within Education",
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("teaching_resources_listing", serializer=DefaultPageSerializer()),
        APIField("teaching_resources_teaser_override"),
        APIField("featured_teaching_resource", serializer=DefaultPageSerializer()),
        APIField("featured_teaching_resource_teaser_override"),
        APIField("education_sessions_listing", serializer=DefaultPageSerializer()),
        APIField("education_sessions_teaser_override"),
        APIField("featured_education_session", serializer=DefaultPageSerializer()),
        APIField("featured_education_session_teaser_override"),
        APIField(
            "latest_teaching_resources", serializer=DefaultPageSerializer(many=True)
        ),
        APIField(
            "latest_education_sessions", serializer=DefaultPageSerializer(many=True)
        ),
        APIField(
            "education_read_more_links",
            serializer=LinkedPageSerializer(many=True),
        ),
    ]

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
            ["education.EducationSessionPage", "education.TeachingResourcePage"],
        ),
    ]

    class Meta:
        verbose_name = "read more link"
        ordering = ["sort_order"]
