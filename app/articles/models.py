from typing import Any, Dict, List, Tuple, Union

from django.conf import settings
from django.db import models
from django.db.models.functions import Coalesce
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from rest_framework import serializers
from taggit.models import ItemBase, TagBase
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from app.ciim.fields import RecordField
from app.ciim.serializers import RecordSerializer
from app.collections.models import TopicalPageMixin
from app.core.blocks import AuthorPromotedPagesBlock, FeaturedCollectionBlock
from app.core.models import (
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    HeroImageMixin,
    PublishedDateMixin,
    RequiredHeroImageMixin,
)
from app.core.serializers import (
    DefaultPageSerializer,
    DetailedImageSerializer,
    ImageSerializer,
    RichTextSerializer,
    TaggableSerializer,
)
from app.core.utils import skos_id_from_text
from app.people.models import AuthorPageMixin

from .blocks import ArticlePageStreamBlock


@register_snippet
class ArticleTag(TagBase):
    free_tagging = False
    skos_id = models.CharField(
        blank=True,
        unique=True,
        db_index=True,
        max_length=100,
        verbose_name="SKOS identifier",
        help_text="Used as the identifier for this tag when sending page metatdata to the CIIM API.",
    )

    class Meta:
        verbose_name = "article tag"
        verbose_name_plural = "article tags"

    panels = (
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("skos_id"),
    )

    def clean(self, *args, **kwargs):
        if not self.skos_id and self.name:
            # Generate a unique skos_id value for new tags
            base_value = skos_id_from_text(self.name)
            self.skos_id = base_value
            i = 2
            while (
                ArticleTag.objects.exclude(id=self.id)
                .filter(skos_id=self.skos_id)
                .exists()
            ):
                self.skos_id = f"{base_value[:97]}_{i}"
                i += 1
        return super().clean(*args, **kwargs)


class TaggedArticle(ItemBase):
    tag = models.ForeignKey(
        ArticleTag, related_name="tagged_article", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class ArticleTagMixin(models.Model):
    """Mixin to add article tags to a Page."""

    article_tag_names = models.TextField(editable=False, null=True)
    tags = ClusterTaggableManager(through=TaggedArticle, blank=True)

    class Meta:
        abstract = True

    promote_panels = [
        FieldPanel("tags"),
    ]

    search_fields = [
        index.SearchField("article_tag_names", boost=2),
    ]

    api_fields = [APIField("tags", serializer=TaggableSerializer())]


class ArticleIndexPage(BasePageWithRequiredIntro):
    """ArticleIndexPage

    This page lists the ArticlePage objects that are children of this page.
    """

    featured_article = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_(
            "Select a page to display in the featured area. This can be an Article, Focused Article or Record Article."
        ),
        verbose_name=_("featured article"),
    )

    featured_pages = StreamField(
        [("featuredpages", FeaturedCollectionBlock())],
        blank=True,
        null=True,
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField(
            "featured_article",
            serializer=DefaultPageSerializer(required_api_fields=["teaser_image"]),
        ),
        APIField("featured_pages"),
    ]

    class Meta:
        verbose_name = _("article index page")

    @cached_property
    def article_pages(self):
        return (
            self.get_children()
            .public()
            .live()
            .order_by(
                Coalesce(
                    "recordarticlepage__published_date",
                    "focusedarticlepage__published_date",
                    "articlepage__published_date",
                )
            )
            .reverse()
            .specific()
        )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        PageChooserPanel(
            "featured_article",
            [
                "articles.ArticlePage",
                "articles.FocusedArticlePage",
                "articles.RecordArticlePage",
            ],
        ),
        FieldPanel("featured_pages"),
    ]

    max_count = 1
    parent_page_types = ["collections.ExplorerIndexPage"]
    subpage_types = [
        "articles.ArticlePage",
        "articles.FocusedArticlePage",
        "articles.RecordArticlePage",
    ]


class ArticlePage(
    TopicalPageMixin,
    RequiredHeroImageMixin,
    ContentWarningMixin,
    PublishedDateMixin,
    ArticleTagMixin,
    BasePageWithRequiredIntro,
):
    """ArticlePage

    The ArticlePage model.
    """

    body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        verbose_name_public = _("the story of")

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + ContentWarningMixin.content_panels
        + [
            FieldPanel("body"),
        ]
    )

    promote_panels = (
        PublishedDateMixin.promote_panels
        + BasePageWithRequiredIntro.promote_panels
        + ArticleTagMixin.promote_panels
        + [
            TopicalPageMixin.get_topics_inlinepanel(),
            TopicalPageMixin.get_time_periods_inlinepanel(),
        ]
    )

    parent_page_types = ["articles.ArticleIndexPage"]
    subpage_types = []

    search_fields = (
        BasePageWithRequiredIntro.search_fields
        + ArticleTagMixin.search_fields
        + [
            index.SearchField("body"),
            index.SearchField("topic_names", boost=1),
            index.SearchField("time_period_names", boost=1),
        ]
    )

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        PublishedDateMixin.get_is_newly_published_apifield(),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + ContentWarningMixin.api_fields
        + ArticleTagMixin.api_fields
        + [
            PublishedDateMixin.get_published_date_apifield(),
            PublishedDateMixin.get_is_newly_published_apifield(),
            APIField("body"),
            APIField(
                "similar_items",
                serializer=DefaultPageSerializer(
                    required_api_fields=["teaser_image"], many=True
                ),
            ),
            APIField(
                "latest_items",
                serializer=DefaultPageSerializer(
                    required_api_fields=["teaser_image"], many=True
                ),
            ),
        ]
        + TopicalPageMixin.api_fields
    )

    def save(self, *args, **kwargs):
        """
        Overrides Page.save() to ensure 'article_tag_names' always reflects the tags() value
        """
        if (
            "update_fields" not in kwargs
            or "article_tag_names" in kwargs["update_fields"]
        ):
            self.article_tag_names = "\n".join(t.name for t in self.tags.all())
        super().save(*args, **kwargs)

    @cached_property
    def similar_items(
        self,
    ) -> Tuple[Union["ArticlePage", "FocusedArticlePage", "RecordArticlePage"], ...]:
        """
        Returns a maximum of three ArticlePages that are tagged with at least
        one of the same ArticleTags. Items should be ordered by the number
        of tags they have in common.
        """
        if not self.article_tag_names:
            # Avoid unncecssary lookups
            return ()

        tag_ids = self.tagged_items.values_list("tag_id", flat=True)
        if not tag_ids:
            # Avoid unncecssary lookups
            return ()

        # Identify other live pages with tags in common
        related_tags = (
            Page.objects.filter(tagged_items__tag_id__in=tag_ids)
            .exact_type(ArticlePage, FocusedArticlePage, RecordArticlePage)
            .live()
            .public()
            .not_page(self)
        )

        return tuple(
            Page.objects.filter(id__in=related_tags).order_by("-first_published_at")[:3]
        )

    @cached_property
    def latest_items(
        self,
    ) -> List[Union["ArticlePage", "FocusedArticlePage", "RecordArticlePage"]]:
        """
        Return the three most recently published ArticlePages,
        excluding this object.
        """

        latest_query_set = []

        for page_type in [ArticlePage, FocusedArticlePage, RecordArticlePage]:
            latest_query_set.extend(
                page_type.objects.live()
                .public()
                .exclude(id__in=[page.id for page in self.similar_items])
                .not_page(self)
                .select_related("teaser_image")
                .prefetch_related("teaser_image__renditions")
            )

        return sorted(latest_query_set, key=lambda x: x.published_date, reverse=True)[
            :3
        ]


class FocusedArticlePage(
    TopicalPageMixin,
    AuthorPageMixin,
    HeroImageMixin,
    ContentWarningMixin,
    PublishedDateMixin,
    ArticleTagMixin,
    BasePageWithRequiredIntro,
):
    """FocusedArticlePage

    The FocusedArticlePage model.
    """

    body = StreamField(ArticlePageStreamBlock, blank=True, null=True)

    class Meta:
        verbose_name = _("focused article")
        verbose_name_plural = _("focused articles")
        verbose_name_public = _("focus on")

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + HeroImageMixin.content_panels
        + ContentWarningMixin.content_panels
        + [
            FieldPanel("body"),
        ]
    )

    promote_panels = (
        PublishedDateMixin.promote_panels
        + BasePageWithRequiredIntro.promote_panels
        + ArticleTagMixin.promote_panels
        + [
            AuthorPageMixin.get_authors_inlinepanel(),
            TopicalPageMixin.get_topics_inlinepanel(),
            TopicalPageMixin.get_time_periods_inlinepanel(),
        ]
    )

    parent_page_types = ["articles.ArticleIndexPage"]
    subpage_types = []

    search_fields = (
        BasePageWithRequiredIntro.search_fields
        + ArticleTagMixin.search_fields
        + [
            index.SearchField("body"),
            index.SearchField("topic_names", boost=1),
            index.SearchField("time_period_names", boost=1),
            index.SearchField("author_names", boost=1),
        ]
    )

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        PublishedDateMixin.get_is_newly_published_apifield(),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + ContentWarningMixin.api_fields
        + ArticleTagMixin.api_fields
        + [
            PublishedDateMixin.get_is_newly_published_apifield(),
            PublishedDateMixin.get_published_date_apifield(),
            APIField("type_label"),
            APIField("body"),
            APIField(
                "similar_items",
                serializer=DefaultPageSerializer(
                    required_api_fields=["teaser_image"], many=True
                ),
            ),
            APIField(
                "latest_items",
                serializer=DefaultPageSerializer(
                    required_api_fields=["teaser_image"], many=True
                ),
            ),
        ]
        + TopicalPageMixin.api_fields
        + AuthorPageMixin.api_fields
    )

    def save(self, *args, **kwargs):
        """
        Overrides Page.save() to ensure 'article_tag_names' always reflects the tags() value
        """
        if (
            "update_fields" not in kwargs
            or "article_tag_names" in kwargs["update_fields"]
        ):
            self.article_tag_names = "\n".join(t.name for t in self.tags.all())
        super().save(*args, **kwargs)

    @cached_property
    def similar_items(
        self,
    ) -> Tuple[Union["ArticlePage", "FocusedArticlePage", "RecordArticlePage"], ...]:
        """
        Returns a maximum of three ArticlePages that are tagged with at least
        one of the same ArticleTags. Items should be ordered by the number
        of tags they have in common.
        """
        if not self.article_tag_names:
            # Avoid unncecssary lookups
            return ()

        tag_ids = self.tagged_items.values_list("tag_id", flat=True)
        if not tag_ids:
            # Avoid unncecssary lookups
            return ()

        # Identify other live pages with tags in common
        related_tags = (
            Page.objects.filter(tagged_items__tag_id__in=tag_ids)
            .exact_type(ArticlePage, FocusedArticlePage, RecordArticlePage)
            .live()
            .public()
            .not_page(self)
        )

        return tuple(
            Page.objects.filter(id__in=related_tags).order_by("-first_published_at")[:3]
        )

    @cached_property
    def latest_items(
        self,
    ) -> List[Union["ArticlePage", "FocusedArticlePage", "RecordArticlePage"]]:
        """
        Return the three most recently published ArticlePages,
        excluding this object.
        """

        latest_query_set = []

        for page_type in [ArticlePage, FocusedArticlePage, RecordArticlePage]:
            latest_query_set.extend(
                page_type.objects.live()
                .public()
                .exclude(id__in=[page.id for page in self.similar_items])
                .not_page(self)
                .select_related("teaser_image")
                .prefetch_related("teaser_image__renditions")
            )

        return sorted(latest_query_set, key=lambda x: x.published_date, reverse=True)[
            :3
        ]


class PageGalleryImage(Orderable):
    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    caption = RichTextField(
        features=["bold", "italic", "link"],
        help_text="An optional caption, which will be displayed directly below the image. This could be used for image sources or for other useful metadata.",
        blank=True,
    )

    class Meta(Orderable.Meta):
        verbose_name = _("gallery image")
        verbose_name_plural = _("gallery images")

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


class GallerySerializer(serializers.ModelSerializer):
    image = DetailedImageSerializer(
        rendition_size="max-1024x1024", background_colour=None
    )
    caption = RichTextSerializer()

    class Meta:
        model = PageGalleryImage
        fields = (
            "image",
            "caption",
        )


class RecordArticlePage(
    TopicalPageMixin,
    ContentWarningMixin,
    PublishedDateMixin,
    ArticleTagMixin,
    BasePageWithRequiredIntro,
):

    parent_page_types = ["articles.ArticleIndexPage"]
    subpage_types = []

    intro_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Square, rotated image to display in the page introduction"),
        verbose_name=_("intro image"),
    )

    record = RecordField(verbose_name=_("record"), db_index=True)
    record.wagtail_reference_index_ignore = True

    date_text = models.CharField(
        verbose_name=_("date text"),
        max_length=100,
        help_text=_("Date(s) related to the record (max. character length: 100)"),
    )

    about = RichTextField(
        verbose_name=_("why this record matters"),
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
    )

    image_library_link = models.URLField(
        blank=True,
        verbose_name="Image library link",
        help_text="Link to an external image library",
    )

    print_on_demand_link = models.URLField(
        blank=True,
        verbose_name="Print on demand link",
        help_text="Link to an external print on demand service",
    )

    gallery_heading = models.CharField(
        verbose_name=_("gallery heading"),
        max_length=250,
        blank=True,
        null=True,
        help_text=_("Optional heading for the gallery"),
    )

    featured_highlight_gallery = models.ForeignKey(
        "collections.HighlightGalleryPage",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("featured highlight gallery"),
    )

    featured_article = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_(
            "Select a page to display in the featured area. This can be an Article, Focused Article or Record Article."
        ),
        verbose_name=_("featured article"),
    )

    promoted_links = StreamField(
        [("promoted_link", AuthorPromotedPagesBlock())],
        max_num=1,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("record article")
        verbose_name_plural = _("record articles")
        verbose_name_public = _("record revealed")

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + [
            FieldPanel("intro_image"),
        ]
        + ContentWarningMixin.content_panels
        + [
            MultiFieldPanel(
                heading="Image Gallery",
                classname="collapsible",
                children=[
                    FieldPanel("gallery_heading"),
                    InlinePanel(
                        "gallery_images",
                        heading="Image Gallery",
                        label="Item",
                        min_num=1,
                        max_num=6,
                    ),
                ],
            ),
            MultiFieldPanel(
                heading="Body",
                children=[
                    FieldPanel("record"),
                    FieldPanel("date_text"),
                    FieldPanel("about"),
                    FieldPanel("image_library_link"),
                    FieldPanel("print_on_demand_link"),
                ],
            ),
            FieldPanel("featured_highlight_gallery"),
            PageChooserPanel(
                "featured_article",
                [
                    "articles.ArticlePage",
                    "articles.FocusedArticlePage",
                    "articles.RecordArticlePage",
                ],
            ),
            FieldPanel("promoted_links"),
        ]
    )

    promote_panels = (
        PublishedDateMixin.promote_panels
        + BasePageWithRequiredIntro.promote_panels
        + ArticleTagMixin.promote_panels
        + [
            TopicalPageMixin.get_topics_inlinepanel(),
            TopicalPageMixin.get_time_periods_inlinepanel(),
        ]
    )

    search_fields = (
        BasePageWithRequiredIntro.search_fields
        + ArticleTagMixin.search_fields
        + [
            index.SearchField("date_text"),
            index.SearchField("about"),
            index.SearchField("topic_names", boost=1),
            index.SearchField("time_period_names", boost=1),
        ]
    )

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        PublishedDateMixin.get_is_newly_published_apifield(),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + ContentWarningMixin.api_fields
        + ArticleTagMixin.api_fields
        + [
            PublishedDateMixin.get_is_newly_published_apifield(),
            PublishedDateMixin.get_published_date_apifield(),
            APIField("type_label"),
            APIField("date_text"),
            APIField("about", serializer=RichTextSerializer()),
            APIField("record", serializer=RecordSerializer()),
            APIField("gallery_heading"),
            APIField("gallery_items", serializer=GallerySerializer(many=True)),
            APIField("image_library_link"),
            APIField("print_on_demand_link"),
            APIField(
                "featured_article",
                serializer=DefaultPageSerializer(required_api_fields=["teaser_image"]),
            ),
            APIField(
                "featured_highlight_gallery",
                serializer=DefaultPageSerializer(
                    required_api_fields=["highlight_cards"]
                ),
            ),
            APIField("promoted_links"),
            APIField(
                "intro_image",
                serializer=ImageSerializer(
                    rendition_size="width-400", background_colour=None
                ),
            ),
        ]
        + TopicalPageMixin.api_fields
    )

    @cached_property
    def gallery_items(self):
        """
        Used to access the page's 'gallery_images' for output. Makes use of
        Django's select_related() and prefetch_related() to efficiently
        prefetch image and rendition data from the database.
        """
        return (
            self.gallery_images.all()
            .select_related("image")
            .prefetch_related("image__renditions")
        )

    def save(self, *args, **kwargs):
        """
        Overrides Page.save() to ensure 'article_tag_names' always reflects the tags() value
        """
        if (
            "update_fields" not in kwargs
            or "article_tag_names" in kwargs["update_fields"]
        ):
            self.article_tag_names = "\n".join(t.name for t in self.tags.all())
        super().save(*args, **kwargs)
