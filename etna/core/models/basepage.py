from typing import Any, Dict

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import options
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Page
from wagtail.search import index
from wagtail_headless_preview.models import HeadlessPreviewMixin

from etna.alerts.models import AlertMixin
from etna.analytics.mixins import DataLayerMixin
from etna.core.cache_control import (
    apply_default_cache_control,
    apply_default_vary_headers,
)
from etna.core.serializers import (
    AliasOfSerializer,
    ImageSerializer,
    MourningSerializer,
    RichTextSerializer,
)

from .mixins import SocialMixin

__all__ = [
    "BasePage",
    "BasePageWithIntro",
    "BasePageWithRequiredIntro",
]

# Tiny hack to allow us to specify a `verbose_name_public` attribute
# on `Meta` classes, which is used in place of `verbose_name`
# for display in the front-end.
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("verbose_name_public",)


@method_decorator(apply_default_vary_headers, name="serve")
@method_decorator(apply_default_cache_control, name="serve")
class BasePage(AlertMixin, SocialMixin, DataLayerMixin, HeadlessPreviewMixin, Page):
    """
    An abstract base model that is used for all Page models within
    the project. Any common fields, Wagtail overrides or custom
    functionality can be added here.
    """

    short_title = models.CharField(
        verbose_name=_("short title"),
        help_text=_(
            "A shorter title for use in breadcrumbs and other navigational elements, where applicable."
        ),
        max_length=30,
        blank=True,
        null=True,
    )

    teaser_text = models.TextField(
        verbose_name=_("teaser text"),
        help_text=_(
            "A short, enticing description of this page. This will appear in promos and under thumbnails around the site."
        ),
        max_length=160,
    )

    teaser_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Image that will appear on thumbnails and promos around the site."),
    )

    # DataLayerMixin overrides
    gtm_content_group = "Page"

    show_publish_date_in_search_results = False

    # Overriding the default/core help_text set in MetadataPageMixin
    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel(
                    "slug",
                    help_text=_(
                        "The name of the page as it will appear at the end of the URL e.g. http://nationalarchives.org.uk/[slug]"
                    ),
                    widget=SlugInput,
                ),
            ],
            _("For search engines"),
        ),
        FieldPanel("short_title"),
    ] + SocialMixin.promote_panels

    settings_panels = Page.settings_panels + AlertMixin.settings_panels

    class Meta:
        abstract = True

    def clean(self, *args, **kwargs):
        if self.short_title and len(self.short_title) > len(self.title):
            raise ValidationError(
                {"short_title": ["The short title must not be longer than the title."]}
            )
        return super().clean(*args, **kwargs)

    @cached_property
    def type_label(cls) -> str:
        """
        Return the label to use for this page type in the front-end,
        with the first letter capitalized for display.
        """
        if cls.has_custom_type_label():
            return capfirst(cls._meta.verbose_name_public)
        return None

    @classmethod
    def has_custom_type_label(cls) -> bool:
        """
        Returns a boolean indicating whether a custom 'verbose_name_public' value
        has been set in `Meta` for this page type.
        """
        return bool(getattr(cls._meta, "verbose_name_public", None))

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Return values that should be included in the Google Analytics datalayer
        when rendering this page.

        Override this method on subclasses to add data that is relevant to a
        specific page type.
        """
        data = super().get_datalayer_data(request)
        data.update(customDimension3=self._meta.verbose_name)
        return data

    @property
    def privacy(self):
        privacy = [r.restriction_type for r in self.get_view_restrictions()]
        if privacy:
            return privacy[0]
        return "public"

    @property
    def mourning_notice(self):
        from etna.home.models import MourningNotice

        return MourningNotice.objects.first()

    @cached_property
    def type(self):
        return self._meta.label

    default_api_fields = [
        APIField("id"),
        APIField("title"),
        APIField("short_title"),
        APIField("url"),
        APIField("full_url"),
        APIField("type"),
        APIField("type_label"),
        APIField("teaser_text"),
        APIField(
            "teaser_image",
            serializer=ImageSerializer("fill-600x400"),
        ),
        APIField("first_published_at"),
        APIField("last_published_at"),
    ]

    api_fields = (
        [APIField("short_title")]
        + AlertMixin.api_fields
        + [
            APIField("type_label"),
            APIField("mourning_notice", serializer=MourningSerializer()),
        ]
    )

    api_meta_fields = [
        APIField("teaser_text"),
        APIField(
            "teaser_image",
            serializer=ImageSerializer("fill-600x400"),
        ),
        APIField("alias_of", serializer=AliasOfSerializer()),
    ] + SocialMixin.api_meta_fields


class BasePageWithIntro(BasePage):
    """
    An abstract base model for more long-form content pages that
    start with a required 'intro'.
    """

    intro = RichTextField(
        verbose_name=_("introductory text"),
        help_text=_(
            "1-2 sentences introducing the subject of the page, and explaining why a user should read on."
        ),
        features=settings.INLINE_RICH_TEXT_FEATURES,
        max_length=300,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    content_panels = BasePage.content_panels + [FieldPanel("intro")]

    search_fields = BasePage.search_fields + [
        index.SearchField("intro", boost=3),
    ]

    api_fields = BasePage.api_fields + [
        APIField("intro", serializer=RichTextSerializer())
    ]


class BasePageWithRequiredIntro(BasePageWithIntro):
    """
    An abstract base model for more long-form content pages that
    start with a required 'intro'.
    """

    intro = RichTextField(
        verbose_name=_("introductory text"),
        help_text=_(
            "1-2 sentences introducing the subject of the page, and explaining why a user should read on."
        ),
        features=settings.INLINE_RICH_TEXT_FEATURES,
        max_length=300,
    )

    class Meta:
        abstract = True
