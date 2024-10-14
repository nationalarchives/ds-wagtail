from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from etna.core.models import (
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    HeroImageMixin,
)
from etna.core.serializers import DateTimeSerializer, DefaultPageSerializer
from etna.people.models import AuthorPageMixin

from .blocks import BlogPostPageStreamBlock


class BlogIndexPage(HeroImageMixin, BasePageWithRequiredIntro):
    """Blog index page

    This is the parent page for all blog posts. It is used to
    display a list of blog posts, and blog pages.
    """

    subpage_types = ["blog.BlogPage"]

    parent_page_types = ["home.HomePage"]

    content_panels = (
        BasePageWithRequiredIntro.content_panels + HeroImageMixin.content_panels
    )

    promote_panels = BasePageWithRequiredIntro.promote_panels

    @cached_property
    def blog_pages(self):
        return BlogPage.objects.all().live().public().specific().order_by("title")

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("blog_pages", serializer=DefaultPageSerializer(many=True))
    ]


class BlogPage(HeroImageMixin, BasePageWithRequiredIntro):
    """Blog page

    This is the parent page for blog posts
    It is used to display a list of the blog posts
    that are children of this page, as well as other
    blogs within this blog.
    """

    subpage_types = ["blog.BlogPostPage", "blog.BlogPage"]

    content_panels = (
        BasePageWithRequiredIntro.content_panels + HeroImageMixin.content_panels
    )

    promote_panels = BasePageWithRequiredIntro.promote_panels

    @cached_property
    def blog_posts(self):
        return (
            self.get_children()
            .type(BlogPostPage)
            .live()
            .public()
            .specific()
            .order_by("-blogpostpage__published_date")
        )

    @cached_property
    def blog_pages(self):
        return (
            self.get_children()
            .type(BlogPage)
            .live()
            .public()
            .specific()
            .order_by("title")
        )

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + [
            APIField("blog_posts", serializer=DefaultPageSerializer(many=True)),
            APIField("blog_pages", serializer=DefaultPageSerializer(many=True)),
        ]
    )


class BlogPostPage(AuthorPageMixin, ContentWarningMixin, BasePageWithRequiredIntro):
    """Blog post page

    This is a blog post page. It is used to display a single blog post.
    """

    parent_page_types = ["blog.BlogPage"]

    body = StreamField(
        BlogPostPageStreamBlock(),
    )

    published_date = models.DateTimeField(
        verbose_name="Published date",
        help_text="The date the blog post was published.",
        default=timezone.now,
    )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("body"),
    ]

    promote_panels = BasePageWithRequiredIntro.promote_panels + [
        FieldPanel("published_date"),
        AuthorPageMixin.get_authors_inlinepanel(),
    ]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("published_date"),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + ContentWarningMixin.api_fields
        + AuthorPageMixin.api_fields
        + [
            APIField("published_date", serializer=DateTimeSerializer()),
            APIField("body"),
        ]
    )
