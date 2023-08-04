from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
)
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from etna.core.models import BasePage
from wagtail.models import Page
from modelcluster.fields import ParentalKey


class AuthorIndexPage(BasePage):
    """Author index page

    This is the parent page for all authors. It is used to
    generate the author index page.
    """

    subpage_types = ["authors.AuthorPage"]

    parent_page_types = ["home.HomePage"]

    @cached_property
    def author_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(AuthorPage)
            .order_by("title")
            .live()
            .specific()[:3]
        )
        


class AuthorPage(BasePage):
    """Author page

    Model to store author details. Including image and a link to
    an external biography page.
    """

    role = models.CharField(blank=True, null=True, max_length=100)
    summary = RichTextField(
        blank=True, null=True, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("role"),
        FieldPanel("summary"),
        FieldPanel("image"),
    ]

    class Meta:
        verbose_name_plural = "Authors"

    parent_page_types = ["authors.AuthorIndexPage"]

    @cached_property
    def authored_focused_articles(self):
        from etna.articles.models import FocusedArticlePage

        return (
            FocusedArticlePage.objects.live()
            .public()
            .filter(pk__in=self.related_page_pks)
            .order_by("-first_published_at")
            .select_related("teaser_image")[:4]
        )
    
    @cached_property
    def related_page_pks(self):
        """
        Returns a list of ids of pages that have used the `PageTimePeriod` inline
        to indicate a relationship with this time period. The values are ordered by:
        - The order in which this time period was specified (more important time periods are specified first)
        - When the page was first published ('more recently added' pages take presendence)
        """
        return tuple(
            self.author_pages.values_list("page_id", flat=True).order_by(
                "-page__first_published_at"
            )
        )


class AuthorTag(models.Model):
    """
    This model allows any page type to be associated with one or more topics
    in a way that retains the order of topics selected.

    The ``sort_order`` field value from ``Orderable`` can be used to pull out
    the 'first' topic to treat as the 'primary topic' for a page, and can also
    used to prioritise items for a list of 'pages related to a topic'.

    Just add `InlinePanel("page_topics")` to a page type's panel
    configuration to use it!
    """

    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="author_tags")
    author = models.ForeignKey(
        AuthorPage,
        verbose_name="author",
        related_name="author_pages",
        on_delete=models.CASCADE,
    )


class AuthorPageMixin:
    """
    A mixin for pages that use the ``PageTopic`` and ``PageTimePeriod`` models
    in order to be associated with one or many topics/time periods. It simply
    adds a few properies to support robust, efficient access the related topic
    and time period pages.
    """

    @classmethod
    def get_authors_inlinepanel(cls, max_num = 1):
        return InlinePanel(
            "author_tags",
            heading="Page author",
            help_text="If the page relates to more than one topic, please add these in order of relevance from most to least.",
            max_num=max_num,
        )

    @cached_property
    def authors(self):
        return tuple(
            item.author
            for item in self.author_tags.select_related("author").filter(
                author__live=True
            )
        )
    
    @cached_property
    def author_item(self):
        try:
            return self.authors[0]
        except IndexError:
            return None
    
    @property
    def author_name(self):
        """
        Returns the titles of all related topics, joined together into one big
        comma-separated string. Ideal for indexing!
        """
        if self.author_item:
            return self.author_item.title
        else:
            return None

    @cached_property
    def authors_alphabetical(self):
        return sorted(self.author, key=lambda item: item.title.lower())