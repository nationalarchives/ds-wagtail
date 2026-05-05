from app.core.models import (
    BasePageWithRequiredIntro,
)
from app.core.serializers import DefaultPageSerializer
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField

from ..serializers import EducationReadMoreLinkSerializer
from .details import EducationSessionPage, TeachingResourcePage


class EducationPage(BasePageWithRequiredIntro):
    """
    A page for listing teaching resources and sessions.
    """

    @cached_property
    def type_label(cls) -> str:
        return "Education"

    @cached_property
    def latest_teaching_resources(self) -> list:
        return list(
            TeachingResourcePage.objects.live()
            .public()
            .order_by("-first_published_at")[:3]
        )

    # TODO: maybe remove cached_property? it will persist and maybe we don't want that
    @cached_property
    def latest_education_sessions(self) -> list:
        upcoming = (
            EducationSessionPage.objects.live()
            .public()
            .filter(start_date__gte=timezone.now())
            .order_by("start_date")
        )

        if upcoming.exists():
            return list(upcoming[:3])

        # If no upcoming, get most recent
        return list(
            EducationSessionPage.objects.live().public().order_by("-start_date")[:3]
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
        verbose_name=_("teaching resource listing page"),
        help_text=_(
            "The teaching resource listing page to display on the Education landing page."
        ),
    )

    teaching_resources_teaser = models.TextField(
        verbose_name=_("teaching resources teaser text"),
        help_text=_(
            "Short text under Explore teaching resources title to entice users to click through"
        ),
        blank=True,
    )

    featured_teaching_resource = models.ForeignKey(
        "education.TeachingResourcePage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("featured teaching resource"),
        help_text=_(
            "Option to add a highlighted teaching resource, particularly for history months etc"
        ),
    )

    featured_teaching_resource_teaser_override = models.TextField(
        verbose_name=_("Featured teaching resource teaser text override"),
        help_text=_("Override text for the featured teaching resource"),
        blank=True,
    )

    # Education sessions section
    education_sessions_listing_page = models.ForeignKey(
        "education.EducationSessionsListingPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("education sessions listing page"),
        help_text=_(
            "The education sessions listing page to display on the Education landing page."
        ),
    )

    education_sessions_teaser = models.TextField(
        verbose_name=_("education sessions teaser text"),
        help_text=_(
            "Short text under Explore education sessions title to entice users to click through"
        ),
        blank=True,
    )

    featured_education_session = models.ForeignKey(
        "education.EducationSessionPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("featured education session"),
        help_text=_("Page picker to highlight a featured education session"),
    )

    featured_education_session_teaser_override = models.TextField(
        verbose_name=_("Featured education session teaser text override"),
        help_text=_("Override text for the featured education session"),
        blank=True,
    )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel("teaching_resources_listing_page"),
                FieldPanel("teaching_resources_teaser"),
                MultiFieldPanel(
                    [
                        PageChooserPanel("featured_teaching_resource"),
                        FieldPanel("featured_teaching_resource_teaser_override"),
                    ],
                    heading=_("Featured resource"),
                ),
            ],
            heading=_("Teaching resources"),
        ),
        MultiFieldPanel(
            [
                PageChooserPanel("education_sessions_listing_page"),
                FieldPanel("education_sessions_teaser"),
                MultiFieldPanel(
                    [
                        PageChooserPanel("featured_education_session"),
                        FieldPanel("featured_education_session_teaser_override"),
                    ],
                    heading=_("Featured session"),
                ),
            ],
            heading=_("Education sessions"),
        ),
        InlinePanel(
            "education_read_more_links",
            heading=_("Read more"),
            help_text=_("Navigation to other sections within Education"),
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("teaching_resources_listing_page", serializer=DefaultPageSerializer()),
        APIField("teaching_resources_teaser"),
        APIField("featured_teaching_resource", serializer=DefaultPageSerializer()),
        APIField("featured_teaching_resource_teaser_override"),
        APIField("education_sessions_listing_page", serializer=DefaultPageSerializer()),
        APIField("education_sessions_teaser"),
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
            serializer=EducationReadMoreLinkSerializer(many=True),
        ),
    ]

    class Meta:
        verbose_name = _("Education landing page")

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
        verbose_name=_("selected page"),
        help_text=_("Navigation to other sections within Education"),
    )

    panels = [
        PageChooserPanel("selected_page"),
    ]

    class Meta:
        verbose_name = _("read more link")
        ordering = ["sort_order"]
