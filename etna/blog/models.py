from django.db import models
from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField

from etna.core.models import (
    BasePage,
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    HeroImageMixin,
    PublishedDateMixin,
)
from etna.core.serializers.pages import DefaultPageSerializer
from etna.people.models import AuthorPageMixin, ExternalAuthorMixin

from .blocks import BlogPostPageStreamBlock


class BlogIndexPage(BasePageWithRequiredIntro):
    """Blog index page

    This is the parent page for all blog posts. It is used to
    display a list of blog posts, and blog pages.
    """

    subpage_types = ["blog.BlogPage", "blog.BlogFeedsPage"]
    parent_page_types = ["home.HomePage"]

    max_count = 1

    @cached_property
    def blogs_feeds_page(self):
        """
        Returns the blogs feeds page.
        """
        return BlogFeedsPage.objects.all().live().first()

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("blogs_feeds_page", serializer=DefaultPageSerializer()),
    ]


class BlogPage(HeroImageMixin, BasePageWithRequiredIntro):
    """Blog page

    This is the parent page for blog posts
    It is used to display a list of the blog posts
    that are children of this page, as well as other
    blogs within this blog.
    """

    custom_type_label = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Override the chip for child blog posts. If left blank, the chip will be the title of the blog.",
        verbose_name="Chip override",
    )

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

    promote_panels = BasePageWithRequiredIntro.promote_panels + [
        FieldPanel("custom_type_label"),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + [APIField("custom_type_label")]
    )


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

    @cached_property
    def type_label(cls) -> str:
        """
        Overrides the type_label method from BasePage, to return the correct
        type label for the blog post page.
        """
        top_level = cls.get_ancestors().type(BlogPage).first().specific
        if not top_level:
            return "Blog post"
        if top_level.custom_type_label:
            return top_level.custom_type_label
        return top_level.title

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + HeroImageMixin.content_panels
        + ContentWarningMixin.content_panels
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


class BlogFeedsPage(BasePage):
    """
    Blog feeds page
    """

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    max_count = 1

    body = RichTextField(
        features=[
            "bold",
            "italic",
            "link",
            "ul",
        ],
        help_text="Body text to appear above the list of feeds.",
        blank=True,
    )

    @cached_property
    def blogs_index(self):
        """
        Returns the top-level blog index.
        """
        return BlogIndexPage.objects.all().live().first()

    @cached_property
    def blogs(self):
        """
        Returns the top-level blogs that are not descendants of other blogs.
        """
        all_blogs = BlogPage.objects.all().live()
        for blog in all_blogs:
            # Ignore all "sub-blogs" (BlogPages which are children of other BlogPages)
            all_blogs = all_blogs.not_descendant_of(blog, inclusive=False)
        return all_blogs

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = BasePage.api_fields + [
        APIField("body"),
        APIField("blogs_index", serializer=DefaultPageSerializer()),
        APIField("blogs", serializer=DefaultPageSerializer(many=True)),
    ]
