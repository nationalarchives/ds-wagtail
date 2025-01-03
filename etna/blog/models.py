from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from etna.core.models import (
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    HeroImageMixin,
    PublishedDateMixin,
)
from etna.people.models import AuthorPageMixin, ExternalAuthorMixin

from .blocks import BlogPostPageStreamBlock


class BlogIndexPage(BasePageWithRequiredIntro):
    """Blog index page

    This is the parent page for all blog posts. It is used to
    display a list of blog posts, and blog pages.
    """

    subpage_types = ["blog.BlogPage"]
    parent_page_types = ["home.HomePage"]

    max_count = 1


class BlogPage(HeroImageMixin, BasePageWithRequiredIntro):
    """Blog page

    This is the parent page for blog posts
    It is used to display a list of the blog posts
    that are children of this page, as well as other
    blogs within this blog.
    """

    parent_page_types = [
        "blog.BlogIndexPage",
        "blog.BlogPage",
        "collections.ExplorerIndexPage",
        "generic_pages.GeneralPage",
        "generic_pages.HubPage",
        "home.HomePage",
    ]
    subpage_types = ["blog.BlogPostPage", "blog.BlogPage"]

    content_panels = (
        BasePageWithRequiredIntro.content_panels + HeroImageMixin.content_panels
    )

    promote_panels = BasePageWithRequiredIntro.promote_panels

    api_fields = BasePageWithRequiredIntro.api_fields + HeroImageMixin.api_fields


class BlogPostPage(
    AuthorPageMixin,
    ExternalAuthorMixin,
    ContentWarningMixin,
    PublishedDateMixin,
    HeroImageMixin,
    BasePageWithRequiredIntro,
):
    """Blog post page

    This is a blog post page. It is used to display a single blog post.
    """

    parent_page_types = ["blog.BlogPage"]

    body = StreamField(
        BlogPostPageStreamBlock(),
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + HeroImageMixin.content_panels
        + [
            FieldPanel("body"),
        ]
    )

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
        + PublishedDateMixin.promote_panels
        + [
            AuthorPageMixin.get_authors_inlinepanel(),
            ExternalAuthorMixin.get_authors_inlinepanel(),
        ]
    )

    default_api_fields = (
        BasePageWithRequiredIntro.default_api_fields
        + AuthorPageMixin.default_api_fields
        + [
            PublishedDateMixin.get_published_date_apifield(),
            PublishedDateMixin.get_is_newly_published_apifield(),
            APIField("last_published_at"),
        ]
    )

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + ContentWarningMixin.api_fields
        + AuthorPageMixin.api_fields
        + ExternalAuthorMixin.api_fields
        + [
            PublishedDateMixin.get_published_date_apifield(),
            PublishedDateMixin.get_is_newly_published_apifield(),
            APIField("body"),
        ]
    )

    class Meta:
        verbose_name = "Blog post page"
        verbose_name_plural = "Blog post pages"
        verbose_name_public = "Blog post"
