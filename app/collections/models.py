from typing import Optional, Tuple

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from rest_framework import serializers
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

from app.ciim.fields import RecordField
from app.ciim.serializers import RecordSerializer
from app.core.models import (
    BasePage,
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    RequiredHeroImageMixin,
)
from app.core.serializers import (
    DefaultPageSerializer,
    DetailedImageSerializer,
    ImageSerializer,
    RichTextSerializer,
)
from app.core.utils import skos_id_from_text

from .blocks import (
    ExplorerIndexPageStreamBlock,
    TopicIndexPageStreamBlock,
)


class Highlight(Orderable):
    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="page_highlights",
    )

    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("image"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("title"),
        help_text=_(
            "The descriptive name of the image. If this image features in a highlights gallery, this title will be visible on the page."
        ),
    )

    record = RecordField(
        verbose_name=_("related record"),
        db_index=True,
        blank=False,
        null=False,
        help_text=_(
            "If the image relates to a specific record, select that record here."
        ),
    )
    record.wagtail_reference_index_ignore = True

    record_dates = models.CharField(
        verbose_name=_("record date(s)"),
        max_length=100,
        blank=False,
        null=False,
        help_text=_("Date(s) related to the selected record (max length: 100 chars)."),
    )

    description = RichTextField(
        verbose_name=_("description"),
        help_text=(
            "This text will appear in highlights galleries. A 100-300 word "
            "description of the story of the record and why it is significant."
        ),
        blank=False,
        null=False,
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
        max_length=900,
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("image"),
        FieldPanel("record"),
        FieldPanel("record_dates"),
        FieldPanel("description"),
    ]


class ExplorerIndexPageSelection(Orderable):
    """A model to allow a list of pages to be selected for display on the Explorer Index Page."""

    page = ParentalKey(
        "collections.ExplorerIndexPage",
        on_delete=models.CASCADE,
        related_name="explorer_index_page_selections",
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="explorer_index_page_selected_pages",
        help_text=_("Select a page to display in the Explorer Index Page."),
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Optional title for the selected page. If left blank, the page title will be used."
        ),
    )

    teaser_text = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Optional teaser text for the selected page. If left blank, the page's teaser text will be displayed."
        ),
    )

    teaser_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_(
            "Optional image to display in the teaser for the selected page. If left blank, the page's teaser image will be displayed."
        ),
    )

    cta_label = models.CharField(
        max_length=50,
        blank=True,
        help_text=_(
            "Optional label for the call to action button. If left blank, 'Read more' will be used."
        ),
        verbose_name="CTA label",
    )

    panels = [
        FieldPanel("selected_page"),
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("teaser_text"),
                FieldPanel("teaser_image"),
                FieldPanel("cta_label"),
            ],
            heading=_("Page link overrides"),
        ),
    ]

    class Meta:
        ordering = ["sort_order"]


class ExplorerIndexPageSelectionSerializer(serializers.Serializer):
    """Serializer for ExplorerIndexPageSelection."""

    def to_representation(self, instance):
        if instance.selected_page:
            representation = {
                "selected_page": DefaultPageSerializer().to_representation(
                    instance.selected_page
                ),
            }
            if instance.title:
                representation["selected_page"]["title"] = instance.title
            if instance.teaser_text:
                representation["selected_page"]["teaser_text"] = instance.teaser_text
            if instance.teaser_image:
                representation["selected_page"][
                    "teaser_image"
                ] = ImageSerializer().to_representation(instance.teaser_image)
            if instance.cta_label:
                representation["cta_label"] = instance.cta_label
            return representation


class ExplorerIndexPage(RequiredHeroImageMixin, BasePageWithRequiredIntro):
    """Collection Explorer landing BasePage.

    This page is the starting point for a user's journey through the collection
    explorer.
    """

    body = StreamField(ExplorerIndexPageStreamBlock, blank=True)

    stories_hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("stories hero image"),
        help_text=_(
            "The stories section hero image to display on the Explorer Index Page."
        ),
    )

    stories_hero_image_caption = RichTextField(
        blank=True, null=True, features=settings.INLINE_RICH_TEXT_FEATURES
    )

    explorer_index_page_selections_title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("The title to display for the Explorer Index Page selections."),
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            FieldPanel("body"),
            MultiFieldPanel(
                [
                    FieldPanel("stories_hero_image"),
                    FieldPanel("stories_hero_image_caption"),
                ],
                heading=_("Stories section"),
            ),
            FieldPanel("explorer_index_page_selections_title"),
            InlinePanel(
                "explorer_index_page_selections",
                label=_("Selected pages for Explorer Index Page"),
                max_num=2,
                help_text=_("Select pages to display on the Explorer Index Page."),
            ),
        ]
    )

    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = [
        "collections.TopicExplorerIndexPage",
        "collections.TimePeriodExplorerIndexPage",
        "articles.ArticleIndexPage",
        "blog.BlogPage",
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + [
            APIField("body"),
            APIField(
                "stories_hero_image",
                serializer=DetailedImageSerializer(rendition_size="fill-1200x480"),
            ),
            APIField(
                "stories_hero_image_small",
                serializer=DetailedImageSerializer(source="stories_hero_image"),
            ),
            APIField("stories_hero_image_caption", serializer=RichTextSerializer()),
            APIField("explorer_index_page_selections_title"),
            APIField(
                "explorer_index_page_selections",
                serializer=ExplorerIndexPageSelectionSerializer(many=True),
            ),
        ]
    )


class TopicExplorerIndexPage(RequiredHeroImageMixin, BasePageWithRequiredIntro):
    """Topic explorer BasePage.

    This page lists all child TopicExplorerPages
    """

    body = StreamField(TopicIndexPageStreamBlock, blank=True)

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            FieldPanel("body"),
        ]
    )

    api_fields = (
        RequiredHeroImageMixin.api_fields
        + BasePageWithRequiredIntro.api_fields
        + [
            APIField("body"),
            APIField(
                "explorer_pages",
                serializer=DefaultPageSerializer(
                    many=True, required_api_fields=["teaser_image"]
                ),
            ),
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
    def explorer_pages(self):
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


class TopicExplorerPage(RequiredHeroImageMixin, BasePageWithRequiredIntro):
    """Topic explorer page.

    This page represents one of the many categories a user may select in the
    collection explorer.

    An explorer page is responsible for listing pages related to its topic/time period,
    which may be a HighlightGallery, Article, or RecordArticle.
    """

    class Meta:
        verbose_name = _("topic page")
        verbose_name_plural = _("topic pages")
        verbose_name_public = _("explore the collection")

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

    skos_id = models.CharField(
        unique=True,
        blank=True,
        db_index=True,
        max_length=100,
        verbose_name="SKOS identifier",
        help_text="Used as the identifier for this topic when sending page metadata to the CIIM API.",
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
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
        ]
    )

    settings_panels = BasePage.settings_panels + [FieldPanel("skos_id")]

    parent_page_types = [
        "collections.TopicExplorerIndexPage",
        "collections.TopicExplorerPage",
    ]
    subpage_types = [
        "collections.HighlightGalleryPage",
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + [
            APIField(
                "featured_article",
                serializer=DefaultPageSerializer(required_api_fields=["teaser_image"]),
            ),
            APIField("skos_id"),
            APIField(
                "related_articles",
                serializer=DefaultPageSerializer(
                    required_api_fields=["teaser_image"], many=True
                ),
            ),
            APIField(
                "related_highlight_gallery_pages",
                serializer=DefaultPageSerializer(
                    required_api_fields=["teaser_image"], many=True
                ),
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

    @cached_property
    def related_articles(self):
        """
        Return a list of related pages for rendering in the related articles section
        of the page. To add another page type, import it and add it to the list.
        """

        from app.articles.models import (
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

        return sorted(page_list, key=lambda x: x.published_date, reverse=True)

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


class TimePeriodExplorerIndexPage(RequiredHeroImageMixin, BasePageWithRequiredIntro):
    """Time period explorer BasePage.

    This page lists all child TimePeriodExplorerPage
    """

    body = StreamField(TopicIndexPageStreamBlock, blank=True)

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            FieldPanel("body"),
        ]
    )

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
    def explorer_pages(self):
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
        + BasePageWithRequiredIntro.api_fields
        + [
            APIField("body"),
            APIField(
                "explorer_pages",
                serializer=DefaultPageSerializer(
                    many=True, required_api_fields=["teaser_image"]
                ),
            ),
        ]
    )


class TimePeriodExplorerPage(RequiredHeroImageMixin, BasePageWithRequiredIntro):
    """Time period BasePage.

    This page represents one of the many categories a user may select in the
    collection explorer.

    An explorer page is responsible for listing pages related to its topic/time period,
    which may be a HighlightGallery, Article, or RecordArticle.
    """

    class Meta:
        verbose_name = _("time period page")
        verbose_name_plural = _("time period pages")
        verbose_name_public = _("explore the collection")

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

    start_year = models.IntegerField(blank=False)
    end_year = models.IntegerField(blank=False)
    content_panels = (
        BasePageWithRequiredIntro.content_panels
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
            FieldPanel("start_year"),
            FieldPanel("end_year"),
        ]
    )

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + [
            APIField(
                "featured_article",
                serializer=DefaultPageSerializer(required_api_fields=["teaser_image"]),
            ),
            APIField(
                "related_articles",
                serializer=DefaultPageSerializer(
                    required_api_fields=["teaser_image"], many=True
                ),
            ),
            APIField(
                "related_highlight_gallery_pages",
                serializer=DefaultPageSerializer(
                    required_api_fields=["teaser_image"], many=True
                ),
            ),
            APIField("start_year"),
            APIField("end_year"),
        ]
    )

    parent_page_types = [
        "collections.TimePeriodExplorerIndexPage",
        "collections.TimePeriodExplorerPage",
    ]
    subpage_types = [
        "collections.HighlightGalleryPage",
    ]

    @cached_property
    def related_articles(self):
        """
        Return a list of related pages for rendering in the related articles section
        of the page. To add another page type, import it and add it to the list.
        """

        from app.articles.models import (
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

        return sorted(page_list, key=lambda x: x.published_date, reverse=True)

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
    def topics(self) -> Tuple[TopicExplorerPage]:
        return tuple(
            item.topic
            for item in self.page_topics.select_related("topic").filter(
                topic__live=True
            )
        )

    @property
    def topic_names(self) -> str:
        """
        Returns the titles of all related topics, joined together into one big
        comma-separated string. Ideal for indexing!
        """
        return ", ".join(item.title for item in self.topics)

    @cached_property
    def time_periods(self) -> Tuple[TimePeriodExplorerPage]:
        return tuple(
            item.time_period
            for item in self.page_time_periods.select_related("time_period").filter(
                time_period__live=True
            )
        )

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


class HighlightSerializer(serializers.ModelSerializer):
    image = DetailedImageSerializer(
        rendition_size="max-1024x1024", background_colour=None
    )
    description = RichTextSerializer()
    record = RecordSerializer()

    class Meta:
        model = Highlight
        fields = ("title", "image", "description", "record", "record_dates")


class HighlightCardSerializer(serializers.Serializer):
    """
    A serializer for the HighlightGalleryPage's `highlight_cards`.

    This is for use in a reference to the page, to display some of the
    highlights on the page.
    """

    def to_representation(self, value):
        return {
            "image": ImageSerializer().to_representation(value.image),
        }


class HighlightGalleryPage(
    TopicalPageMixin, ContentWarningMixin, BasePageWithRequiredIntro
):
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
        BasePageWithRequiredIntro.api_fields
        + ContentWarningMixin.api_fields
        + [
            APIField(
                "featured_article",
                serializer=DefaultPageSerializer(required_api_fields=["teaser_image"]),
            ),
            APIField("highlights", serializer=HighlightSerializer(many=True)),
            APIField("highlight_cards", serializer=HighlightCardSerializer(many=True)),
        ]
        + TopicalPageMixin.api_fields
    )

    class Meta:
        verbose_name = _("highlight gallery page")
        verbose_name_plural = _("highlight gallery pages")
        verbose_name_public = _("in pictures")

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + ContentWarningMixin.content_panels
        + [
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
    )

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("highlight_image_count"),
    ]

    promote_panels = BasePageWithRequiredIntro.promote_panels + [
        TopicalPageMixin.get_topics_inlinepanel(),
        TopicalPageMixin.get_time_periods_inlinepanel(),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("highlights_text", boost=1),
        index.SearchField("topic_names"),
        index.SearchField("time_period_names"),
        index.SearchField("teaser_text"),
    ]

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

    @cached_property
    def highlight_cards(self):
        """
        Used to return a list of cards for use in a reference to the page,
        to display a portion of the highlights on this page.
        """
        return self.highlights[:5]

    @property
    def highlights_text(self) -> str:
        """
        Returns all of the relevant text defined for this page's highlights,
        joined into one giant string to faciliate indexing.
        """
        strings = []
        for item in self.highlights:
            strings.extend([item.image.title, item.description])
        return " | ".join(strings)
