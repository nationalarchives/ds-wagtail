from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Page

from etna.core.models import BasePage


class AuthorIndexPage(BasePage):
    """Author index page

    This is the parent page for all authors. It is used to
    display a list of authors, and to link to individual
    author pages from the list.
    """

    subpage_types = ["authors.AuthorPage"]

    parent_page_types = ["home.HomePage"]

    @cached_property
    def author_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return self.get_children().type(AuthorPage).order_by("title").live().specific()


class AuthorPage(BasePage):
    """Author page

    This page is to be used for an author profile page, where
    we can put info about the author, an image, and then use it
    to link pages to an author.
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
        FieldPanel("image"),
        FieldPanel("role"),
        FieldPanel("summary"),
    ]

    class Meta:
        verbose_name_plural = "Authors"

    parent_page_types = ["authors.AuthorIndexPage"]
    subpage_types = []

    @cached_property
    def authored_focused_articles(self):
        from etna.articles.models import FocusedArticlePage

        return (
            FocusedArticlePage.objects.live()
            .public()
            .filter(pk__in=self.related_page_pks)
            .order_by("-first_published_at")
            .select_related("teaser_image")
        )

    @cached_property
    def related_page_pks(self):
        """
        Returns a list of ids of pages that have used the `AuthorTag` inline
        to indicate a relationship with this author. The values are ordered by
        when the page was first published ('more recently added' pages take presendence)
        """
        return tuple(
            self.author_pages.values_list("page_id", flat=True).order_by(
                "-page__first_published_at"
            )
        )


class AuthorTag(models.Model):
    """
    This model allows any page type to be associated with an author page.

    Just add `AuthorPageMixin.get_authors_inlinepanel()` to a page type's panel
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
    A mixin for pages that uses the ``AuthorTag`` model
    in order to be associated with an author.
    """

    @classmethod
    def get_authors_inlinepanel(cls, max_num=1):
        return InlinePanel(
            "author_tags",
            heading="Page author",
            help_text="Select the author for this page.",
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
        Returns the title of the author to be used for indexing
        """
        if self.author_item:
            return self.author_item.title
        else:
            return None
