from typing import Any, Dict

from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images import get_image_model_string
from wagtail.images.api.fields import ImageRenditionField
from wagtail.models import Page

from rest_framework import serializers

from etna.core.blocks.paragraph import APIRichTextField
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
        return (
            self.get_children()
            .type(AuthorPage)
            .order_by("title")
            .live()
            .specific()
        )


# TODO: Make better
class AuthorPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = (
            "id",
            "title",
            "url_path",
        )


class AuthorPage(BasePage):
    """Author page

    This page is to be used for an author profile page, where
    we can put info about the author, an image, and then use it
    to link pages to an author.
    """

    role = models.CharField(blank=True, null=True, max_length=100)
    summary = APIRichTextField(
        blank=True, null=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
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
        verbose_name = "Author page"
        verbose_name_plural = "Author pages"

    # DataLayerMixin overrides
    gtm_content_group = "Author page"

    parent_page_types = ["authors.AuthorIndexPage"]
    subpage_types = []

    api_fields = BasePage.api_fields + [
        APIField("role"),
        APIField("summary"),
        APIField("image"),
        APIField(
            "authored_focused_articles",
            serializer=AuthorPageSerializer(many=True),
        ),
        APIField(
            "image_jpg",
            serializer=ImageRenditionField(
                "fill-512x512|format-jpeg|jpegquality-60", source="image"
            ),
        ),
        APIField(
            "image_small_jpg",
            serializer=ImageRenditionField(
                "fill-128x128|format-jpeg|jpegquality-60", source="image"
            ),
        ),
    ]

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

    def get_datalayer_data(self, request: HttpRequest) -> Dict[str, Any]:
        data = super().get_datalayer_data(request)
        data.update(customDimension3="Author page")
        return data


class AuthorTag(models.Model):
    """
    This model allows any page type to be associated with an author page.

    Add a ForeignKey with a fitting related_name (e.g. `focused_articles`
    for `FocusedArticlePage`) to the page's model to use this.
    """

    page = ParentalKey(
        Page, on_delete=models.CASCADE, related_name="author_tags"
    )
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
    def get_authors_inlinepanel(cls, max_num=3):
        return InlinePanel(
            "author_tags",
            heading="Page author",
            help_text="Select the author of this page.",
            max_num=max_num,
        )

    @cached_property
    def authors(self):
        if author_item := self.author_tags.select_related("author").filter(
            author__live=True
        ):
            return author_item

    @property
    def author_names(self):
        """
        Returns the title of the authors to be used for indexing
        """
        if self.authors:
            return ", ".join([author.author.title for author in self.authors])
