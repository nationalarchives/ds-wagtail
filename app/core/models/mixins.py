from datetime import timedelta

from django.db import models
from django.http import HttpRequest
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Site
from wagtail_headless_preview.models import (
    HeadlessPreviewMixin,
    get_client_root_url_from_site,
)

from app.core.serializers import (
    DateTimeSerializer,
    DetailedImageSerializer,
    ImageSerializer,
    RichTextSerializer,
)
from app.core.styling import BrandColourChoices, HeroColourChoices, HeroLayoutChoices

from .forms import RequiredHeroImagePageForm

__all__ = [
    "AccentColourMixin",
    "ContentWarningMixin",
    "HeroImageMixin",
    "HeroLayoutMixin",
    "HeroStyleMixin",
    "PublishedDateMixin",
    "RequiredHeroImageMixin",
    "SidebarMixin",
    "SocialMixin",
]


class ContentWarningMixin(models.Model):
    """Mixin to allow editors to add content warnings to a page."""

    custom_warning_text = RichTextField(
        verbose_name="custom content warning text (optional)",
        features=["link"],
        blank=True,
        help_text=("If specified, will be used for the content warning."),
    )

    content_panels = [
        FieldPanel("custom_warning_text"),
    ]

    api_fields = [
        APIField("custom_warning_text", serializer=RichTextSerializer()),
    ]

    class Meta:
        abstract = True


class PublishedDateMixin(models.Model):
    """Mixin to add a published date to a Page."""

    new_label_display_for_days = 21

    published_date = models.DateTimeField(
        verbose_name="Published date",
        help_text="The date the page was published to the public.",
        default=timezone.now,
    )

    @cached_property
    def is_newly_published(self):
        expiry_date = timezone.now().date() - timedelta(
            days=self.new_label_display_for_days
        )
        if self.published_date:
            if self.published_date.date() > expiry_date:
                return True
        return False

    class Meta:
        abstract = True

    promote_panels = [
        FieldPanel("published_date"),
    ]

    @classmethod
    def get_published_date_apifield(cls) -> APIField:
        return APIField("published_date", serializer=DateTimeSerializer())

    @classmethod
    def get_is_newly_published_apifield(cls) -> APIField:
        return APIField("is_newly_published")


class HeroImageMixin(models.Model):
    """Mixin to add hero_image attribute to a Page."""

    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    hero_image_caption = RichTextField(
        verbose_name="hero image caption (optional)",
        features=["bold", "italic", "link"],
        blank=True,
        help_text=(
            "An optional caption for hero images. This could be used for image sources or for other useful metadata."
        ),
    )

    class Meta:
        abstract = True

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("hero_image_caption"),
            ],
            heading="Hero image",
        )
    ]

    api_fields = [
        APIField("hero_image_caption", serializer=RichTextSerializer()),
        APIField(
            "hero_image",
            serializer=DetailedImageSerializer("fill-1800x720"),
        ),
        APIField(
            "hero_image_small",
            serializer=DetailedImageSerializer("fill-900x600", source="hero_image"),
        ),
    ]


class RequiredHeroImageMixin(HeroImageMixin):
    """Mixin to add hero_image attribute to a Page, and make it required."""

    class Meta:
        abstract = True

    base_form_class = RequiredHeroImagePageForm


class AccentColourMixin(models.Model):
    """Mixin to add accent_colour attribute to a Page."""

    accent_colour = models.CharField(
        max_length=20,
        default=BrandColourChoices.NONE,
        verbose_name=_("page accent colour"),
        help_text=_("The accent colour of the page where relevant."),
        choices=BrandColourChoices.choices,
    )

    class Meta:
        abstract = True

    content_panels = [
        FieldPanel("accent_colour"),
    ]

    api_fields = [
        APIField("accent_colour"),
    ]


class HeroLayoutMixin(models.Model):
    """Mixin to choose the layout of the hero component"""

    hero_layout = models.CharField(
        max_length=20,
        default=HeroLayoutChoices.DEFAULT,
        verbose_name=_("hero layout"),
        help_text=_("The layout of the hero component."),
        choices=HeroLayoutChoices.choices,
    )

    class Meta:
        abstract = True

    content_panels = [
        FieldPanel("hero_layout"),
    ]

    api_fields = [
        APIField("hero_layout"),
    ]


class HeroStyleMixin(models.Model):
    """Mixin to choose the accent colour of the hero component"""

    hero_style = models.CharField(
        max_length=20,
        default=HeroColourChoices.NONE,
        verbose_name=_("hero component colour"),
        help_text=_("The accent colour of the hero component."),
        choices=HeroColourChoices.choices,
    )

    class Meta:
        abstract = True

    content_panels = [
        FieldPanel("hero_style"),
    ]

    api_fields = [
        APIField("hero_style"),
    ]


class SidebarMixin(models.Model):
    """Mixin to add sidebar options to a Page."""

    page_sidebar = models.CharField(
        choices=[
            ("contents", "Contents"),
            ("sections", "Sections"),
            ("section_tabs", "Section tabs"),
            ("pages", "Pages"),
            ("pages_tabs", "Pages tabs"),
        ],
        help_text=mark_safe(
            "Select the sidebar style for this page. For more information, see the <a href='https://nationalarchives.github.io/design-system/components/sidebar/'>sidebar documentation</a>."
        ),
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    settings_panels = [
        FieldPanel("page_sidebar"),
    ]

    api_fields = [
        APIField("page_sidebar"),
    ]


class SocialMixin(models.Model):
    """Mixin to add social media sharing options to a Page."""

    search_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("OpenGraph image"),
        help_text=_(
            "Image that will appear when this page is shared on social media. This will default to the teaser image if left blank."
        ),
    )

    twitter_og_title = models.CharField(
        verbose_name=_("Twitter OpenGraph title"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("If left blank, the OpenGraph title will be used."),
    )
    twitter_og_description = models.TextField(
        verbose_name=_("Twitter OpenGraph description"),
        blank=True,
        null=True,
        help_text=_("If left blank, the OpenGraph description will be used."),
    )
    twitter_og_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Twitter OpenGraph image"),
        help_text=_("If left blank, the OpenGraph image will be used."),
    )

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel(
                    "seo_title",
                    help_text=_(
                        "The name of the page displayed on search engine results as the clickable headline and when shared on social media."
                    ),
                ),
                FieldPanel(
                    "search_description",
                    help_text=_(
                        "The descriptive text displayed underneath a headline in search engine results and when shared on social media."
                    ),
                ),
                FieldPanel("search_image"),
            ],
            heading="Base OpenGraph data",
        ),
        MultiFieldPanel(
            [
                FieldPanel("twitter_og_title"),
                FieldPanel("twitter_og_description"),
                FieldPanel("twitter_og_image"),
            ],
            heading="Twitter OpenGraph data",
        ),
    ]

    api_meta_fields = [
        APIField(
            "teaser_image_square",
            serializer=ImageSerializer("fill-512x512", source="teaser_image"),
        ),
        APIField("seo_title"),
        APIField("search_description"),
        APIField(
            "search_image",
            serializer=ImageSerializer("fill-1200x630"),
        ),
        APIField("twitter_og_title"),
        APIField("twitter_og_description"),
        APIField(
            "twitter_og_image",
            serializer=ImageSerializer("fill-1200x630"),
        ),
    ]


class CustomHeadlessPreviewMixin(HeadlessPreviewMixin):
    def get_client_root_url(self, request: HttpRequest) -> str:
        """
        Uses the WAGTAIL_HEADLESS_PREVIEW settings to determine the preview URL.
        Falls back to the site from the request if the page has no specific site.
        This respects the WAGTAIL_HEADLESS_PREVIEW_URL environment variable.
        """
        site = self.get_site() or Site.find_for_request(request)
        return get_client_root_url_from_site(site)
