from django.utils.functional import cached_property

from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from etna.core.models import (
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    HeroImageMixin,
)
from etna.core.serializers import DefaultPageSerializer
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
        return (
            BlogPage.objects.all()
            .order_by("-first_published_at")
            .live()
            .public()
            .specific()
        )

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
            .order_by("-first_published_at")
            .live()
            .public()
            .specific()
        )

    @cached_property
    def blog_pages(self):
        return (
            self.get_children()
            .type(BlogPage)
            .order_by("-first_published_at")
            .live()
            .public()
            .specific()
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

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("body"),
    ]

    promote_panels = BasePageWithRequiredIntro.promote_panels + [
        AuthorPageMixin.get_authors_inlinepanel()
    ]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("first_published_at"),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + ContentWarningMixin.api_fields
        + AuthorPageMixin.api_fields
        + [
            APIField("body"),
        ]
    )
