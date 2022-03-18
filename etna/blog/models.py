from django.db import models

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from taggit.models import ItemBase

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page
from wagtail.search import index

from ..collections.models import ThemeTag, CategoryTag
from ..richtext.fields import RichTextField


class TaggedThemeBlogPageItem(ItemBase):
    tag = models.ForeignKey(
        ThemeTag, related_name="tagged_blog_page_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "blog.BlogPage",
        on_delete=models.CASCADE,
        related_name="tagged_blog_page_items",
    )


class TaggedCategoryBlogPageItem(ItemBase):
    tag = models.ForeignKey(
        CategoryTag, related_name="tagged_blog_page_items", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        "blog.BlogPage",
        on_delete=models.CASCADE,
        related_name="tagged_category_items",
    )


class BlogIndexPage(Page):
    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPage"]


class BlogPage(Page):
    source_url = models.URLField()
    body = RichTextField()
    date_published = models.DateTimeField()
    content_tags = ClusterTaggableManager(
        through=TaggedCategoryBlogPageItem, blank=True
    )
    theme_tags = ClusterTaggableManager(through=TaggedThemeBlogPageItem, blank=True)

    content_panels = [
        FieldPanel("source_url"),
        FieldPanel("title"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        FieldPanel("content_tags", heading="Content tags"),
        FieldPanel("theme_tags", heading="Theme tags"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("source_url"),
        index.SearchField("body"),
        index.RelatedFields(
            "content_tags",
            [
                index.SearchField("name"),
                index.FilterField("slug"),
            ],
        ),
        index.RelatedFields(
            "theme_tags",
            [
                index.SearchField("name"),
                index.FilterField("slug"),
            ],
        ),
    ]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    def __str__(self):
        return self.title
