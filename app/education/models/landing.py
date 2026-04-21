from app.core.models import (
    BasePageWithRequiredIntro,
)
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.models import Orderable

from .details import EducationSessionPage, KeyStageTag, TeachingResourcePage


class EducationPage(BasePageWithRequiredIntro):
    """
    A page for listing teaching resources and sessions.
    """

    @cached_property
    def type_label(cls) -> str:
        return "Education"

    # Teaching resources section
    teaching_resource_listing_page = models.ForeignKey(
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

    @cached_property
    def latest_teaching_resources(self) -> list:
        """Returns 3 most recently published teaching resources"""
        return list(
            TeachingResourcePage.objects.live()
            .public()
            .order_by("-first_published_at")[:3]
        )

    @cached_property
    def latest_education_sessions(self) -> list:
        """Returns 3 upcoming sessions, or most recent if no upcoming"""

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

    # Panels, pages, parents and children
    parent_page_types = [
        "home.HomePage",
    ]

    subpage_types = [
        "education.EducationSessionsListingPage",
        "education.TeachingResourcesListingPage",
    ]

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel("teaching_resource_listing_page"),
                FieldPanel("teaching_resources_teaser"),
                MultiFieldPanel(
                    [
                        PageChooserPanel("featured_teaching_resource"),
                        FieldPanel("featured_teaching_resource_teaser_override"),
                    ],
                    heading=_("Featured"),
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
                    heading=_("Featured"),
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

    class Meta:
        verbose_name = _("Education landing page")
