from app.core.fields.choosers import PartnerLogoField
from app.core.models import (
    AccentColourMixin,
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    HeroLayoutMixin,
    HeroStyleMixin,
    LocationSerializer,
    RequiredHeroImageMixin,
)
from app.core.serializers import (
    DefaultPageSerializer,
    RichTextSerializer,
)
from app.core.serializers.partner_logos import PartnerLogoSerializer
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
    TitleFieldPanel,
)
from wagtail.models import Orderable


class KeyStageTag(Orderable):
    """
    This model is used to tag Education pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="page_key_stage_tags",
    )

    key_stage = models.ForeignKey(
        "education.KeyStage",
        on_delete=models.CASCADE,
        related_name="key_stage",
        verbose_name=_("Key stage"),
        help_text=_("The key stage of the page."),
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return f"{self.page.title}: {self.key_stage.name}"


class KeyStage(models.Model):
    """A model per key stage"""

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Key stage")
        verbose_name_plural = _("Key stages")

    def __str__(self):
        return self.name


class TeachingResourcePage(BasePageWithRequiredIntro):
    """A page to display a teaching resource"""

    key_stage = models.ForeignKey(
        "education.KeyStage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("key stage"),
    )

    parent_page_types = [
        "education.TeachingResourcesListingPage",
    ]


class EducationSessionPage(BasePageWithRequiredIntro):
    """A page to display an education session"""

    key_stage = models.ForeignKey(
        "education.KeyStage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("key stage"),
    )

    parent_page_types = [
        "education.EducationSessionsListingPage",
    ]


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
