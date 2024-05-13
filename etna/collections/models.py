from typing import Any, Dict, List, Optional, Tuple, Union

from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page
from wagtail.search import index

from rest_framework import serializers

from etna.core.serializers import (
    DefaultPageSerializer,
    HighlightImageSerializer,
)

from ..alerts.models import AlertMixin
from ..core.models import (
    BasePage,
    BasePageWithIntro,
    ContentWarningMixin,
    RequiredHeroImageMixin,
)
from ..core.utils import skos_id_from_text
from .blocks import (
    ExplorerIndexPageStreamBlock,
    FeaturedArticlesBlock,
    TimePeriodExplorerPageStreamBlock,
    TopicExplorerPageStreamBlock,
    TopicIndexPageStreamBlock,
)


class Highlight(Orderable):
    page = ParentalKey(
        "wagtailcore.Page", on_delete=models.CASCADE, related_name="page_highlights"
    )
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("image"),
    )

    alt_text = models.CharField(
        verbose_name=_("alternative text"),
        max_length=100,
        null=True,
        help_text=mark_safe(
            'Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">Check the guidance for tips on writing alt text</a>.'
        ),
    )

    panels = [
        FieldPanel("image"),
        FieldPanel("alt_text"),
    ]

    def clean(self) -> None:
        if self.image:
            if not self.image.record or not self.image.description:
                raise ValidationError(
                    {
                        "image": [
                            "Only images with a 'record' and a 'description' specified can be used for highlights."
                        ]
                    }
                )
        return super().clean()


class ExplorerIndexPage(AlertMixin, BasePageWithIntro):
    """Collection Explorer landing BasePage.

    This page is the starting point for a user's journey through the collection
    explorer.
    """

    body = StreamField(ExplorerIndexPageStreamBlock, blank=True)

    articles_title = models.CharField(
        max_length=100,
        blank=True,
        default="Stories from the collection",
        help_text=_("The title to display for the articles section."),
    )

    articles_introduction = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("The introduction to display for the articles section."),
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

    featured_articles = StreamField(
        [("featuredarticles", FeaturedArticlesBlock())],
        blank=True,
        null=True,
    )

    content_panels = BasePageWithIntro.content_panels + [
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("articles_title"),
                FieldPanel("articles_introduction"),
                PageChooserPanel(
                    "featured_article",
                    [
                        "articles.ArticlePage",
                        "articles.FocusedArticlePage",
                        "articles.RecordArticlePage",
                    ],
                ),
                FieldPanel("featured_articles"),
            ],
            heading=_("Articles section"),
        ),
    ]

    settings_panels = BasePageWithIntro.settings_panels + AlertMixin.settings_panels

    parent_page_types = ["home.HomePage"]
    subpage_types = [
        "collections.TopicExplorerIndexPage",
        "collections.TimePeriodExplorerIndexPage",
        "articles.ArticleIndexPage",
    ]

    # DataLayerMixin overrides
    gtm_content_group = "Explore the collection"

    api_fields = (
        AlertMixin.api_fields
        + BasePageWithIntro.api_fields
        + [
            APIField("body"),
            APIField("articles_title"),
            APIField("articles_introduction"),
            APIField(
                "featured_article",
                serializer=DefaultPageSerializer(required_api_fields=["teaser_image"]),
            ),
            APIField("featured_articles"),
        ]
    )


class TopicExplorerIndexPage(RequiredHeroImageMixin, BasePageWithIntro):
    """Topic explorer BasePage.

    This page lists all child TopicExplorerPages
    """

    body = StreamField(TopicIndexPageStreamBlock, blank=True)

    content_panels = (
        BasePageWithIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            FieldPanel("body"),
        ]
    )

    # DataLayerMixin overrides
    gtm_content_group = "Explore the collection"

    api_fields = (
        RequiredHeroImageMixin.api_fields
        + BasePageWithIntro.api_fields
        + [
            APIField("body"),
        ]
    )

    @cached_property
    def featured_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(TopicExplorerPage)
            .order_by("?")
            .live()
            .specific()[:3]
        )

    @cached_property
    def topic_explorer_pages(self):
        """Fetch all child TopicExplorerPages for display in list."""
        return (
            self.get_children()
            .type(TopicExplorerPage)
            .order_by("title")
            .live()
            .specific()
        )

    max_count = 1
    parent_page_types = ["collections.ExplorerIndexPage"]
    subpage_types = [
        "collections.TopicExplorerPage",
    ]


class TopicExplorerPage(RequiredHeroImageMixin, AlertMixin, BasePageWithIntro):
    """Topic explorer page.

    This page represents one of the many categories a user may select in the
    collection explorer.

    An explorer page is responsible for listing pages related to its topic/time period,
    which may be a HighlightGallery, Article, or RecordArticle.
    """

    class Meta:
        verbose_name = _("topic page")
        verbose_name_plural = _("topic pages")
        verbose_name_public = _("explore by topic")

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

    body = StreamField(TopicExplorerPageStreamBlock, blank=True)

    skos_id = models.CharField(
        unique=True,
        blank=True,
        db_index=True,
        max_length=100,
        verbose_name="SKOS identifier",
        help_text="Used as the identifier for this topic when sending page metadata to the CIIM API.",
    )

    content_panels = (
        BasePageWithIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            PageChooserPanel(
                "featured_article",
                [
                    "articles.ArticlePage",
                    "articles.FocusedArticlePage",
                    "articles.RecordArticlePage",
                ],
            ),
            FieldPanel("body"),
        ]
    )

    settings_panels = (
        BasePage.settings_panels + [FieldPanel("skos_id")] + AlertMixin.settings_panels
    )

    # DataLayerMixin overrides
    gtm_content_group = "Explore the collection"

    parent_page_types = [
        "collections.TopicExplorerIndexPage",
        "collections.TopicExplorerPage",
    ]
    subpage_types = [
        "collections.TopicExplorerPage",
        "collections.HighlightGalleryPage",
    ]

    api_fields = (
        RequiredHeroImageMixin.api_fields
        + AlertMixin.api_fields
        + BasePageWithIntro.api_fields
        + [
            APIField("body"),
            APIField(
                "featured_article",
                serializer=DefaultPageSerializer(required_api_fields=["teaser_image"]),
            ),
            APIField("skos_id"),
            APIField("related_articles", serializer=DefaultPageSerializer(many=True)),
            APIField(
                "related_highlight_gallery_pages",
                serializer=DefaultPageSerializer(many=True),
            ),
        ]
    )

    def clean(self, *args, **kwargs):
        if not self.skos_id and self.title:
            # Generate a unique skos_id value for new pages
            base_value = skos_id_from_text(self.title[:100])
            self.skos_id = base_value
            i = 2
            while (
                TopicExplorerPage.objects.exclude(id=self.id)
                .filter(skos_id=self.skos_id)
                .exists()
            ):
                self.skos_id = f"{base_value[:97]}_{i}"
                i += 1
        return super().clean(*args, **kwargs)

    def with_content_json(self, content):
        """
        Overrides :meth:`Page.with_content_json` to always take the ``skos_id``
        value from the page object.
        """
        obj = super().with_content_json(content)
        obj.skos_id = self.skos_id
        return obj

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        data.update(
            customDimension4=self.title,
        )
        return data

    @cached_property
    def related_articles(self):
        """
        Return a list of related pages for rendering in the related articles section
        of the page. To add another page type, import it and add it to the list.
        """

        from etna.articles.models import (
            ArticlePage,
            FocusedArticlePage,
            RecordArticlePage,
        )

        page_list = []

        for page_type in [ArticlePage, FocusedArticlePage, RecordArticlePage]:
            page_list.extend(
                page_type.objects.exclude(pk=self.featured_article_id)
                .filter(pk__in=self.related_page_pks)
                .live()
                .public()
                .select_related("teaser_image")
                .prefetch_related("teaser_image__renditions")
            )

        return sorted(page_list, key=lambda x: x.newly_published_at, reverse=True)

    @cached_property
    def related_highlight_gallery_pages(self):
        return (
            HighlightGalleryPage.objects.live()
            .public()
            .filter(pk__in=self.related_page_pks)
            .order_by("title")
            .select_related("teaser_image")
        )

    @cached_property
    def related_page_pks(self) -> Tuple[int]:
        """
        Returns a list of ids of pages that have used the `PageTopic` inline
        to indicate a relationship with this topic. The values are ordered by:
        - The order in which this topic was specified (more important topics are specified first)
        - When the page was first published ('more recently added' pages take presendence)
        """
        return tuple(
            self.topic_pages.values_list("page_id", flat=True).order_by(
                "sort_order", "-page__first_published_at"
            )
        )


class TimePeriodExplorerIndexPage(RequiredHeroImageMixin, BasePageWithIntro):
    """Time period explorer BasePage.

    This page lists all child TimePeriodExplorerPage
    """

    body = StreamField(TopicIndexPageStreamBlock, blank=True)

    content_panels = (
        BasePageWithIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            FieldPanel("body"),
        ]
    )

    # DataLayerMixin overrides
    gtm_content_group = "Explore the collection"

    @cached_property
    def featured_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(TimePeriodExplorerPage)
            .order_by("?")
            .live()
            .specific()[:3]
        )

    @cached_property
    def time_period_explorer_pages(self):
        """Fetch all child TimePeriodExplorerPages for display in list."""
        return (
            self.get_children()
            .type(TimePeriodExplorerPage)
            .order_by("timeperiodexplorerpage__start_year")
            .live()
            .specific()
        )

    max_count = 1
    parent_page_types = ["collections.ExplorerIndexPage"]
    subpage_types = [
        "collections.TimePeriodExplorerPage",
    ]
    api_fields = (
        RequiredHeroImageMixin.api_fields
        + BasePageWithIntro.api_fields
        + [
            APIField("body"),
        ]
    )


class TimePeriodExplorerPage(RequiredHeroImageMixin, AlertMixin, BasePageWithIntro):
    """Time period BasePage.

    This page represents one of the many categories a user may select in the
    collection explorer.

    An explorer page is responsible for listing pages related to its topic/time period,
    which may be a HighlightGallery, Article, or RecordArticle.
    """

    class Meta:
        verbose_name = _("time period page")
        verbose_name_plural = _("time period pages")
        verbose_name_public = _("explore by time period")

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

    body = StreamField(TimePeriodExplorerPageStreamBlock, blank=True)
    start_year = models.IntegerField(blank=False)
    end_year = models.IntegerField(blank=False)
    content_panels = (
        BasePageWithIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            PageChooserPanel(
                "featured_article",
                [
                    "articles.ArticlePage",
                    "articles.FocusedArticlePage",
                    "articles.RecordArticlePage",
                ],
            ),
            FieldPanel("body"),
            FieldPanel("start_year"),
            FieldPanel("end_year"),
        ]
    )

    api_fields = (
        RequiredHeroImageMixin.api_fields
        + AlertMixin.api_fields
        + BasePageWithIntro.api_fields
        + [
            APIField("body"),
            APIField("related_articles", serializer=DefaultPageSerializer(many=True)),
            APIField(
                "related_highlight_gallery_pages",
                serializer=DefaultPageSerializer(many=True),
            ),
            APIField("start_year"),
            APIField("end_year"),
        ]
    )

    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

    # DataLayerMixin overrides
    gtm_content_group = "Explore the collection"

    parent_page_types = [
        "collections.TimePeriodExplorerIndexPage",
        "collections.TimePeriodExplorerPage",
    ]
    subpage_types = [
        "collections.TimePeriodExplorerPage",
        "collections.HighlightGalleryPage",
    ]

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        data.update(
            customDimension7=self.title,
        )
        return data

    @cached_property
    def related_articles(self):
        """
        Return a list of related pages for rendering in the related articles section
        of the page. To add another page type, import it and add it to the list.
        """

        from etna.articles.models import (
            ArticlePage,
            FocusedArticlePage,
            RecordArticlePage,
        )

        page_list = []

        for page_type in [ArticlePage, FocusedArticlePage, RecordArticlePage]:
            page_list.extend(
                page_type.objects.exclude(pk=self.featured_article_id)
                .filter(pk__in=self.related_page_pks)
                .live()
                .public()
                .select_related("teaser_image")
                .prefetch_related("teaser_image__renditions")
            )

        return sorted(page_list, key=lambda x: x.newly_published_at, reverse=True)

    @cached_property
    def related_highlight_gallery_pages(self):
        return (
            HighlightGalleryPage.objects.live()
            .public()
            .filter(pk__in=self.related_page_pks)
            .order_by("title")
            .select_related("teaser_image")
        )

    @cached_property
    def related_page_pks(self) -> Tuple[int]:
        """
        Returns a list of ids of pages that have used the `PageTimePeriod` inline
        to indicate a relationship with this time period. The values are ordered by:
        - The order in which this time period was specified (more important time periods are specified first)
        - When the page was first published ('more recently added' pages take presendence)
        """
        return tuple(
            self.time_period_pages.values_list("page_id", flat=True).order_by(
                "sort_order", "-page__first_published_at"
            )
        )


class PageTopic(Orderable):
    """
    This model allows any page type to be associated with one or more topics
    in a way that retains the order of topics selected.

    The ``sort_order`` field value from ``Orderable`` can be used to pull out
    the 'first' topic to treat as the 'primary topic' for a page, and can also
    used to prioritise items for a list of 'pages related to a topic'.

    Just add `InlinePanel("page_topics")` to a page type's panel
    configuration to use it!
    """

    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="page_topics")
    topic = models.ForeignKey(
        TopicExplorerPage,
        verbose_name=_("topic"),
        related_name="topic_pages",
        on_delete=models.CASCADE,
    )


class PageTimePeriod(Orderable):
    """
    This model allows any page type to be associated with one or more topics
    in a way that retains the order of topics selected.

    The ``sort_order`` field value from ``Orderable`` can be used to pull out
    the 'first' topic to treat as the 'primary topic' for a page, and can also
    used to prioritise items for a list of 'pages related to a topic'.

    Just add `InlinePanel("page_time_periods")` to a page type's panel
    configuration to use it!
    """

    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="page_time_periods")
    time_period = models.ForeignKey(
        TimePeriodExplorerPage,
        verbose_name=_("time period"),
        related_name="time_period_pages",
        on_delete=models.CASCADE,
    )


class TopicalPageMixin:
    """
    A mixin for pages that use the ``PageTopic`` and ``PageTimePeriod`` models
    in order to be associated with one or many topics/time periods. It simply
    adds a few properies to support robust, efficient access the related topic
    and time period pages.
    """

    api_fields = [
        APIField(
            "topics",
            serializer=DefaultPageSerializer(
                required_api_fields=["teaser_image"], many=True
            ),
        ),
        APIField(
            "time_periods",
            serializer=DefaultPageSerializer(
                required_api_fields=["teaser_image"], many=True
            ),
        ),
    ]

    @classmethod
    def get_time_periods_inlinepanel(cls, max_num: Optional[int] = 4) -> InlinePanel:
        return InlinePanel(
            "page_time_periods",
            heading=_("Related time periods"),
            help_text=_(
                "If the page relates to more than one time period, please add these in order of relevance from most to least"
            ),
            max_num=max_num,
        )

    @classmethod
    def get_topics_inlinepanel(cls, max_num: Optional[int] = 4) -> InlinePanel:
        return InlinePanel(
            "page_topics",
            heading=_("Related topics"),
            help_text=_(
                "If the page relates to more than one topic, please add these in order of relevance from most to least."
            ),
            max_num=max_num,
        )

    @cached_property
    def primary_topic(self) -> Union[TopicExplorerPage, None]:
        try:
            return self.topics[0]
        except IndexError:
            return None

    @cached_property
    def topics(self) -> Tuple[TopicExplorerPage]:
        return tuple(
            item.topic
            for item in self.page_topics.select_related("topic").filter(
                topic__live=True
            )
        )

    @cached_property
    def topics_alphabetical(self) -> List[TopicExplorerPage]:
        return sorted(self.topic, key=lambda item: item.title.lower())

    @property
    def topic_names(self) -> str:
        """
        Returns the titles of all related topics, joined together into one big
        comma-separated string. Ideal for indexing!
        """
        return ", ".join(item.title for item in self.topics)

    @cached_property
    def primary_time_period(self) -> Union[TimePeriodExplorerPage, None]:
        try:
            return self.time_periods[0]
        except IndexError:
            return None

    @cached_property
    def time_periods(self) -> Tuple[TimePeriodExplorerPage]:
        return tuple(
            item.time_period
            for item in self.page_time_periods.select_related("time_period").filter(
                time_period__live=True
            )
        )

    @cached_property
    def time_periods_chronological(self) -> List[TimePeriodExplorerPage]:
        return sorted(self.time_periods, key=lambda item: item.start_year)

    @property
    def time_period_names(self) -> str:
        """
        Returns the titles of all related time periods, joined together into
        one big comma-separated string. Ideal for indexing!
        """
        return ", ".join(item.title for item in self.time_periods)

    @cached_property
    def highlight_image_count(self):
        return self.highlights.count()


# TODO: Make better
class HighlightSerializer(serializers.ModelSerializer):
    image = HighlightImageSerializer()

    class Meta:
        model = Highlight
        fields = (
            "image",
            "alt_text",
        )


class HighlightGalleryPage(TopicalPageMixin, ContentWarningMixin, BasePageWithIntro):
    parent_page_types = [TimePeriodExplorerPage, TopicExplorerPage]
    subpage_types = []

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

    api_fields = (
        BasePageWithIntro.api_fields
        + ContentWarningMixin.api_fields
        + [
            APIField(
                "featured_article",
                serializer=DefaultPageSerializer(required_api_fields=["teaser_image"]),
            ),
            APIField("highlights", serializer=HighlightSerializer(many=True)),
        ]
        + TopicalPageMixin.api_fields
    )

    class Meta:
        verbose_name = _("highlight gallery page")
        verbose_name_plural = _("highlight gallery pages")
        verbose_name_public = _("in pictures")

    content_panels = BasePageWithIntro.content_panels + [
        MultiFieldPanel(
            heading="Content Warning Options",
            classname="collapsible",
            children=[
                FieldPanel("display_content_warning"),
                FieldPanel("custom_warning_text"),
            ],
        ),
        InlinePanel(
            "page_highlights",
            heading=_("Highlights"),
            label=_("Item"),
            max_num=15,
        ),
        PageChooserPanel(
            "featured_article",
            [
                "articles.ArticlePage",
                "articles.FocusedArticlePage",
                "articles.RecordArticlePage",
            ],
        ),
    ]

    promote_panels = BasePageWithIntro.promote_panels + [
        TopicalPageMixin.get_topics_inlinepanel(),
        TopicalPageMixin.get_time_periods_inlinepanel(),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("highlights_text", boost=1),
        index.SearchField("topic_names"),
        index.SearchField("time_period_names"),
        index.SearchField("teaser_text"),
    ]

    gtm_content_group = "Explore the collection"

    @cached_property
    def highlights(self):
        """
        Used to access the page's 'highlights' for output. Makes use of
        Django's select_related() and prefetch_related() to efficiently
        prefetch image and rendition data from the database.
        """
        return (
            self.page_highlights.exclude(image__isnull=True)
            .select_related("image")
            .prefetch_related("image__renditions")
        )

    @property
    def highlights_text(self) -> str:
        """
        Returns all of the relevant text defined for this page's highlights,
        joined into one giant string to faciliate indexing.
        """
        strings = []
        for item in self.highlights:
            strings.extend([item.image.title, item.image.description])
        return " | ".join(strings)

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        data.update(
            customDimension4="; ".join(obj.title for obj in self.topics),
            customDimension7="; ".join(obj.title for obj in self.time_periods),
        )
        return data
