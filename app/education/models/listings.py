from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField

from app.core.models import (
    BasePageWithRequiredIntro,
)
from app.core.serializers import DefaultPageSerializer


class TeachingResourcesListingPage(BasePageWithRequiredIntro):
    """
    A page for displaying education/teaching resources.
    """

    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.TeachingResourcePage",
    ]

    max_count = 1

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

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                PageChooserPanel("featured_teaching_resource"),
                FieldPanel("featured_teaching_resource_teaser_override"),
            ],
            heading="Featured teaching resource",
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("featured_teaching_resource", serializer=DefaultPageSerializer()),
        APIField("featured_teaching_resource_teaser_override"),
    ]

    class Meta:
        verbose_name = "Teaching Resources listing page"


class EducationSessionsListingPage(BasePageWithRequiredIntro):
    """
    A page for displaying education sessions.
    """

    parent_page_types = [
        "education.EducationPage",
    ]

    subpage_types = [
        "education.EducationSessionPage",
    ]

    max_count = 1

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
                PageChooserPanel("featured_education_session"),
                FieldPanel("featured_education_session_teaser_override"),
            ],
            heading="Featured education session",
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("featured_education_session", serializer=DefaultPageSerializer()),
        APIField("featured_education_session_teaser_override"),
    ]

    class Meta:
        verbose_name = "Education Sessions listing page"
