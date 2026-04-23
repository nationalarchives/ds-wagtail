from app.core.blocks.paragraph import APIRichTextBlock
from app.core.models import (
    BasePageWithRequiredIntro,
)
from app.core.serializers import DefaultPageSerializer
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import StreamField


class TeachingResourcesListingPage(BasePageWithRequiredIntro):
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
        "education.TeachingResourcePage",
    ]

    max_count = 1

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

    web_archive_promo = StreamField(
        [("web_archive_promo", APIRichTextBlock(features=["bold", "italic", "link"]))],
        verbose_name=_("web archive promo text"),
        help_text=_(
            "Text block highlighting that old resources can be found in the web archive with a link to the archived old Education site. "
        ),
        blank=True,
        null=True,
    )

    newsletter_sign_up_text = models.TextField(
        verbose_name=_("newsletter sign up text"),
        help_text=_(
            "Text block encouraging users to sign up for the education newsletter."
        ),
        blank=True,
    )

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

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("featured_teaching_resource", serializer=DefaultPageSerializer()),
        APIField("featured_teaching_resource_teaser_override"),
        APIField("web_archive_promo"),
        APIField("newsletter_sign_up_text"),
    ]

    class Meta:
        verbose_name = _("Teaching Resources listing page")


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

    max_count = 1

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

    newsletter_sign_up_text = models.TextField(
        verbose_name=_("newsletter sign up text"),
        help_text=_(
            "Text block encouraging users to sign up for the education newsletter."
        ),
        blank=True,
    )

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

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("featured_education_session", serializer=DefaultPageSerializer()),
        APIField("featured_education_session_teaser_override"),
        APIField("newsletter_sign_up_text"),
    ]

    class Meta:
        verbose_name = _("Education Sessions listing page")
