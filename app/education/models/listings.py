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
    InlinePanel,
    PageChooserPanel,
    MultiFieldPanel,
)
from wagtail.api import APIField
from wagtail.models import Page
from app.core.utils import get_specific_listings


class EducationSessionsListingPage(BasePageWithRequiredIntro):

# Filter by:


# Time period
    """
    A page for displaying education sessions.
    """

    @cached_property
    def type_label(cls) -> str:
        return "Education Resource"

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


    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.TeachingResourcePage",
    ]

    class Meta:
        verbose_name = _("Education Resources listing page")

    max_count = 1


class EducationSessionsListingPage(BasePageWithRequiredIntro):
    """
    A page for displaying education sessions.
    """

    @cached_property
    def type_label(cls) -> str:
        return "Education Session"

    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.EducationSessionPage",
    ]

    class Meta:
        verbose_name = _("Education Sessions listing page")

    max_count = 1
