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
)
from wagtail.api import APIField
from wagtail.models import Page


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
        verbose_name = _("Education Sessions Listing page")

    max_count = 1


class EducationResourcesListingPage(BasePageWithRequiredIntro):
    """
    A page for displaying education/teaching resources.
    """
    @cached_property
    def type_label(cls) -> str:
        return "Education Resource"

    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.EducationResourcePage",
    ]

    class Meta:
        verbose_name = _("Education Resources Listing page")

    max_count = 1