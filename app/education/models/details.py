
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
    TabbedInterface,
    TitleFieldPanel,
)

from wagtail.models import Orderable



class KeyStageTag(Orderable):
    """
    This model is used to tag education pages.
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


class EducationResourcePage(BasePageWithRequiredIntro):
    parent_page_types = [
        "education.EducationResourcesListingPage",
    ]


class EducationSessionPage(BasePageWithRequiredIntro):
    parent_page_types = [
        "education.EducationSessionsListingPage",
    ]

