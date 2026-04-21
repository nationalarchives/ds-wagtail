import datetime

from app.core.models import (
    BasePageWithRequiredIntro,
)
from app.core.serializers import (
    DefaultPageSerializer,
)
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Page

from .details import TeachingResourcePage

# Search and filter [resources page]

# Filter by:

# Key stage

# Time period

# Theme

# See taxonomy


class TeachingResourcesListingPage(BasePageWithRequiredIntro):
    """
    A page for displaying education/teaching resources.
    """

    @cached_property
    def type_label(cls) -> str:
        return "Education Resource"

    # TODO: read-only panels for these how can this become a display panel? maybe it should be in both places?
    # @cached_property
    # def featured_resource(self):
    #     # Get parent EducationPage
    #     parent = self.get_parent()

    #     if parent and hasattr(parent, "featured_teaching_resource"):
    #         if parent.featured_teaching_resource:
    #             return parent.featured_teaching_resource

    #     # Default to most recently published resource
    #     return (
    #         TeachingResourcePage.objects.live()
    #         .public()
    #         .order_by("-first_published_at")
    #         .first()
    #     )

    # @cached_property
    # def featured_resource_teaser(self):
    #     parent = self.get_parent()

    #     if parent and hasattr(parent, "featured_teaching_resource_teaser_override"):
    #         if parent.featured_teaching_resource_teaser_override:
    #             return parent.featured_teaching_resource_teaser_override

    #     return None

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

    web_archive_promo = RichTextField(
        verbose_name=_("web archive promo text"),
        help_text=_(
            "Text block highlighting that old resources can be found in the web archive with a link to the archived old Education site. "
        ),
        blank=True,
    )

    # TODO: should this be hardcoded? how does what's on do it
    newsletter_sign_up_text = models.TextField(
        verbose_name=_("newsletter sign up text"),
        help_text=_(
            "Text block encouraging users to sign up for the education newsletter."
        ),
        blank=True,
    )

    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.TeachingResourcePage",
    ]

    class Meta:
        verbose_name = _("Teaching Resources listing page")

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel("featured_teaching_resource"),
                FieldPanel("featured_teaching_resource_teaser_override"),
            ],
            heading=_("Featured teaching resource"),
        ),
        FieldPanel("web_archive_promo"),
        FieldPanel("newsletter_sign_up_text"),
    ]


class EducationSessionsListingPage(BasePageWithRequiredIntro):
    """
    A page for displaying education sessions.
    """

    @cached_property
    def type_label(cls) -> str:
        return "Education Session"

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

    # TODO: should this be hardcoded? how does what's on do it
    newsletter_sign_up_text = models.TextField(
        verbose_name=_("newsletter sign up text"),
        help_text=_(
            "Text block encouraging users to sign up for the education newsletter."
        ),
        blank=True,
    )

    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.EducationSessionPage",
    ]

    class Meta:
        verbose_name = _("Education Sessions listing page")

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel("featured_education_session"),
                FieldPanel("featured_education_session_teaser_override"),
            ],
            heading=_("Featured education session"),
        ),
        FieldPanel("newsletter_sign_up_text"),
    ]
