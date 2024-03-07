from typing import Any, Dict
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models import options
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.images.api.fields import ImageRenditionField
from wagtail.models import Page
from wagtail.search import index

from wagtail_headless_preview.models import HeadlessPreviewMixin
from wagtailmetadata.models import MetadataPageMixin

from etna.analytics.mixins import DataLayerMixin
from etna.core.cache_control import (
    apply_default_cache_control,
    apply_default_vary_headers,
)
from etna.core.serializers import RichTextSerializer

__all__ = [
    "BasePage",
    "BasePageWithIntro",
]

# Tiny hack to allow us to specify a `verbose_name_public` attribute
# on `Meta` classes, which is used in place of `verbose_name`
# for display in the front-end.
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("verbose_name_public",)


@method_decorator(apply_default_vary_headers, name="serve")
@method_decorator(apply_default_cache_control, name="serve")
class BasePage(MetadataPageMixin, DataLayerMixin, Page, HeadlessPreviewMixin):
    """
    An abstract base model that is used for all Page models within
    the project. Any common fields, Wagtail overrides or custom
    functionality can be added here.
    """

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

    uuid = models.UUIDField("UUID", unique=True, default=uuid4, editable=False)

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
                FieldPanel("seo_title"),
                FieldPanel(
                    "search_description",
                    help_text=_(
                        "The descriptive text displayed underneath a headline in search engine results and when shared on social media."
                    ),
                ),
                FieldPanel(
                    "search_image",
                    help_text=_(
                        "Image that will appear as a promo when this page is shared on social media."
                    ),
                ),
            ],
            _("For search engines"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_in_menus"),
            ],
            _("For site menus"),
        ),
        FieldPanel("teaser_image"),
        FieldPanel("teaser_text"),
    ]

    class Meta:
        abstract = True

    @classmethod
    def type_label(cls) -> str:
        """
        Return the label to use for this page type in the front-end,
        with the first letter capitalized for display.
        """
        if cls.has_custom_type_label():
            label = cls._meta.verbose_name_public
        else:
            label = cls._meta.verbose_name
            if label.lower().endswith(" page"):
                label = label[:-5]
        return capfirst(label)

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

    api_fields = [
        APIField("type_label"),
        APIField("teaser_image"),
        APIField("teaser_text"),
        APIField(
            "teaser_image_jpg",
            serializer=ImageRenditionField(
                "fill-600x400|format-jpeg|jpegquality-60", source="teaser_image"
            ),
        ),
        APIField(
            "teaser_image_webp",
            serializer=ImageRenditionField(
                "fill-600x400|format-webp", source="teaser_image"
            ),
        ),
        APIField(
            "teaser_image_large_jpg",
            serializer=ImageRenditionField(
                "fill-1200x800|format-jpeg|jpegquality-60", source="teaser_image"
            ),
        ),
        APIField(
            "teaser_image_large_webp",
            serializer=ImageRenditionField(
                "fill-1200x800|format-webp", source="teaser_image"
            ),
        ),
        APIField(
            "teaser_image_square_jpg",
            serializer=ImageRenditionField(
                "fill-512x512|format-jpeg|jpegquality-60", source="teaser_image"
            ),
        ),
        APIField(
            "teaser_image_square_webp",
            serializer=ImageRenditionField(
                "fill-512x512|format-webp", source="teaser_image"
            ),
        ),
    ]


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
