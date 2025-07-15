from typing import Any, Dict

from django.conf import settings
from django.db import models
from django.http import HttpRequest
from django.utils.functional import cached_property
from modelcluster.fields import ParentalKey
from rest_framework import serializers
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Page

from app.core.models import BasePage
from app.core.serializers import (
    DefaultPageSerializer,
    ImageSerializer,
    RichTextSerializer,
    SimplePageSerializer,
)

from .blocks import ResearchSummaryStreamBlock

ROLE_CHOICES = {
    "author": "Author",
    "researcher": "Researcher",
}


class PeopleIndexPage(BasePage):
    """People index page

    This is the parent page for all people. It is used to
    display a list of people, and to link to individual
    people pages from the list.
    """

    max_count = 1
    subpage_types = ["people.PersonPage"]

    parent_page_types = ["home.HomePage"]

    api_fields = BasePage.api_fields + [
        APIField("people_pages", serializer=DefaultPageSerializer(many=True))
    ]

    @cached_property
    def people_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(PersonPage)
            .order_by("personpage__last_name")
            .live()
            .public()
            .specific()
        )


class ShopItem(models.Model):
    """Shop item model

    This model is used to represent a shop item.
    """

    page = ParentalKey(
        "PersonPage",
        on_delete=models.CASCADE,
        related_name="shop_items",
    )
    title = models.CharField(max_length=255)
    url = models.URLField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Shop item"
        verbose_name_plural = "Shop items"

    api_fields = [
        APIField("title"),
        APIField("url"),
        APIField("price"),
        APIField("image", serializer=ImageSerializer(rendition_size="fill-600x400")),
    ]


class PersonPage(BasePage):
    """Person page

    This page is to be used for a profile page, where
    we can put info about the person, an image, and then use it
    to link pages to a person, or as a reference to the person.
    """

    image = models.ForeignKey(
        get_image_model_string(),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    role = models.CharField(max_length=100)

    summary = RichTextField(features=settings.RESTRICTED_RICH_TEXT_FEATURES)

    research_summary = StreamField(ResearchSummaryStreamBlock, blank=True, null=True)

    archived_blog_url = models.URLField(
        blank=True,
        null=True,
        help_text="Link to the author's blog on the web archive",
    )

    first_name = models.CharField(
        max_length=255,
    )
    last_name = models.CharField(
        max_length=255,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("image"),
        FieldPanel("role"),
        FieldPanel("summary"),
        FieldPanel("research_summary"),
        InlinePanel("shop_items", label="Shop items"),
        FieldPanel("archived_blog_url"),
    ]

    promote_panels = [
        MultiFieldPanel(
            [FieldPanel("first_name"), FieldPanel("last_name")],
            heading="Person details",
        ),
    ] + BasePage.promote_panels

    class Meta:
        verbose_name = "Person page"
        verbose_name_plural = "People pages"

    parent_page_types = ["people.PeopleIndexPage"]
    subpage_types = []

    default_api_fields = BasePage.default_api_fields + [
        APIField("role"),
        APIField("image", serializer=ImageSerializer(rendition_size="fill-512x512")),
        APIField(
            "image_small",
            serializer=ImageSerializer(rendition_size="fill-128x128", source="image"),
        ),
        APIField("first_name"),
        APIField("last_name"),
        APIField("role_tags"),
        APIField("slug"),
    ]

    api_fields = BasePage.api_fields + [
        APIField("first_name"),
        APIField("last_name"),
        APIField("role"),
        APIField("role_tags"),
        APIField("image", serializer=ImageSerializer(rendition_size="fill-512x512")),
        APIField(
            "image_small",
            serializer=ImageSerializer(rendition_size="fill-128x128", source="image"),
        ),
        APIField("summary", serializer=RichTextSerializer()),
        APIField("research_summary"),
        APIField(
            "shop_items",
        ),
        APIField("archived_blog_url"),
    ]

    @cached_property
    def authored_focused_articles(self):
        from app.articles.models import FocusedArticlePage
        from app.blog.models import BlogPostPage

        return (
            Page.objects.type(FocusedArticlePage, BlogPostPage)
            .live()
            .public()
            .filter(pk__in=self.related_page_pks)
            .order_by("-first_published_at")
        )

    @cached_property
    def related_page_pks(self) -> tuple[int]:
        """
        Returns a list of ids of pages that have used the `AuthorTag` inline
        to indicate a relationship with this author. The values are ordered by
        when the page was first published ('more recently added' pages take presendence)
        """
        return tuple(
            self.people_pages.values_list("page_id", flat=True).order_by(
                "-page__first_published_at"
            )
        )

    @cached_property
    def is_author(self) -> bool:
        """
        def is_X() is going to be a value to help with
        the logic behind the role tags - an easier way
        to check if a person is X role.
        """
        if self.authored_focused_articles:
            return True
        return False

    @cached_property
    def is_researcher(self) -> bool:
        if self.research_summary:
            return True
        return False

    @cached_property
    def role_tags(self) -> list[Dict[str, str]]:
        roles = []
        for role, value in ROLE_CHOICES.items():
            if getattr(self, f"is_{role}"):
                roles.append({"slug": role, "name": value})
        return roles


class AuthorTag(models.Model):
    """
    This model allows any page type to be associated with an author page.

    Add a ForeignKey with a fitting related_name (e.g. `focused_articles`
    for `FocusedArticlePage`) to the page's model to use this.
    """

    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="author_tags")
    author = models.ForeignKey(
        PersonPage,
        verbose_name="author",
        related_name="people_pages",
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
        return tuple(
            item.author
            for item in self.author_tags.select_related("author")
            .filter(author__live=True)
            .order_by("author__last_name")
        )

    @property
    def author_names(self):
        """
        Returns the title of the authors to be used for indexing
        """
        if self.authors:
            return ", ".join([author.title for author in self.authors])

    default_api_fields = [
        APIField(
            "authors",
            serializer=SimplePageSerializer(many=True),
        )
    ]

    api_fields = [
        APIField(
            "authors",
            serializer=DefaultPageSerializer(required_api_fields=["image"], many=True),
        )
    ]


class ExternalAuthorTag(models.Model):
    """
    This model allows any page type to be associated with an external author.
    External authors will not be listed on the People pages, but can be
    added to pages via their name, a description, and an image.
    """

    @cached_property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    page = ParentalKey(
        Page, on_delete=models.CASCADE, related_name="external_author_tags"
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
        blank=True,
    )


class ExternalAuthorSerializer(serializers.ModelSerializer):
    image = ImageSerializer(rendition_size="fill-128x128")

    class Meta:
        model = ExternalAuthorTag
        fields = (
            "first_name",
            "last_name",
            "name",
            "description",
            "image",
        )


class ExternalAuthorMixin:
    """
    A mixin for pages that allow us to add external authors
    to the page.
    """

    @classmethod
    def get_authors_inlinepanel(cls, max_num=3):
        return InlinePanel(
            "external_author_tags",
            heading="External author",
            help_text="Add external authors to this page.",
            max_num=max_num,
        )

    @cached_property
    def external_authors(self):
        return self.external_author_tags.order_by("last_name")

    api_fields = [
        APIField("external_authors", serializer=ExternalAuthorSerializer(many=True)),
    ]
