from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField

from etna.core.models import (
    BasePageWithIntro,
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    HeroImageMixin,
)

from etna.people.models import AuthorPageMixin

class BlogIndexPage(HeroImageMixin, BasePageWithRequiredIntro):
    """Blog index page

    This is the parent page for all blog posts. It is used to
    display a list of blog posts, and blog pages.
    """

    subpage_types = ["blog.BlogPostPage"] # TBC

    parent_page_types = ["home.HomePage"] # TBC


    # @cached_property
    # def blog_posts(self):
    #     """Return a sample of child pages for rendering in teaser."""
    #     return (
    #         self.get_children()
    #         .type(BlogPostPage)
    #         .order_by("-first_published_at")
    #         .live()
    #         .public()
    #         .specific()
    #     )

    # api_fields = BasePageWithIntro.api_fields + [
    #     APIField("blog_posts", serializer=DefaultPageSerializer(many=True))
    # ]


class BlogPage(HeroImageMixin, BasePageWithRequiredIntro):
    """Blog page
    
    This is the parent page for blog posts
    It is used to display a list of the blog posts
    that are children of this page, as well as other
    blogs within this blog.
    """

    subpage_types = ["blog.BlogPostPage", "blog.BlogPage"]

    # @cached_property
    # def blog_posts(self):
    #     """Return a sample of child pages for rendering in teaser."""
    #     return (
    #         self.get_children()
    #         .type(BlogPostPage)
    #         .order_by("-first_published_at")
    #         .live()
    #         .public()
    #         .specific()
    #     )

    # api_fields = BasePageWithIntro.api_fields + [
    #     APIField("blog_posts", serializer=DefaultPageSerializer(many=True))
    # ]

class BlogPostPage(AuthorPageMixin, ContentWarningMixin, BasePageWithIntro):
    """Blog post page

    This is a blog post page. It is used to display a single blog post.
    """

    parent_page_types = ["blog.BlogPage"]