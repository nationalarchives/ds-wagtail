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
from wagtail.models import Page
from app.core.utils import get_specific_listings
from wagtail.fields import RichTextField

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

    #TODO: read-only panels for these how can this become a display panel? maybe it should be in both places?
    @cached_property
    def featured_resource(self):
        # Get parent EducationPage
        parent = self.get_parent()
        
        if parent and hasattr(parent, "featured_teaching_resource"):
            if parent.featured_teaching_resource:
                return parent.featured_teaching_resource
        
        # Default to most recently published resource
        recent_resources = get_specific_listings(
            page_types=["education.TeachingResourcePage"],
            filters={},
            order_by="first_published_at",
            reverse=True,
        )
        return recent_resources[0] if recent_resources else None

    @cached_property
    def featured_resource_teaser(self):
        parent = self.get_parent()
        
        if parent and hasattr(parent, 'featured_teaching_resource_teaser_override'):
            if parent.featured_teaching_resource_teaser_override:
                return parent.featured_teaching_resource_teaser_override
        
        return None

    # Education sessions section
    web_archive_promo = RichTextField(
        verbose_name=_("web archive promo text"),
        help_text=_(
            "Text block highlighting that old resources can be found in the web archive with a link to the archived old Education site. "
        ),
        blank=True,
    )

    #TODO: should this be hardcoded? how does what's on do it
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
        verbose_name = _("Education Resources listing page")

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [   
                #TODO: implement this properly/figure out what's actually wanted
                HelpPanel(
                    content=_(
                        "The featured teaching resource is selected from the parent "
                        "<strong>Education landing page admin</strong>. If no resource is selected there, "
                        "the most recently published resource will be shown automatically."
                    ),
                ),
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


    #TODO: should this be hardcoded? how does what's on do it
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
                #TODO: implement this properly/figure out what's actually wanted
                HelpPanel(
                    content=_(
                        "The featured education session is selected from the parent "
                        "<strong>Education landing page admin</strong>. If no resource is selected there, "
                        "the most recently published resource will be shown automatically."
                    ),
                ),
            ],
            heading=_("Featured education session"),
        ),
        FieldPanel("newsletter_sign_up_text"),
    ]
