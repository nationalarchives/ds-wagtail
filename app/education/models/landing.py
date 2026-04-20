from app.core.models import (
    BasePageWithRequiredIntro,
)
from django.db import models
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


class EducationPage(BasePageWithRequiredIntro):
    """
    A page for listing teaching resources and sessions.
    """

    @cached_property
    def type_label(cls) -> str:
        return "Education"

    # Teaching resources section
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
        verbose_name=_("teaching resource teaser text override"),
        help_text=_("Override text for the featured teaching resource"),
        blank=True,
    )

    # Education sessions section
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
        verbose_name=_("education session teaser text override"),
        help_text=_("Override text for the featured education session"),
        blank=True,
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
        InlinePanel(
            "education_page_selections",
            heading=_("Page selections"),
            help_text=_("Select pages to display on the Education page."),
        ),
        MultiFieldPanel(
            [
                FieldPanel("teaching_resources_teaser"),
                PageChooserPanel("featured_teaching_resource"),
                FieldPanel("featured_teaching_resource_teaser_override"),
            ],
            heading=_("Teaching resources"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("education_sessions_teaser"),
                PageChooserPanel("featured_education_session"),
                FieldPanel("featured_education_session_teaser_override"),
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


class EducationPageSelection(Orderable):
    """
    This model is used to select a page to display on the Education page.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="education_page_selections",
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
        help_text=_("The page to display on the Education page."),
    )

    panels = [
        PageChooserPanel(
            "selected_page",
            page_type=[
                "education.TeachingResourcesListingPage",
                "education.EducationSessionsListingPage",
            ],
        ),
    ]

    class Meta:
        verbose_name = _("selection")
        ordering = ["sort_order"]
