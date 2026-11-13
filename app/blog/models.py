from django.db import models
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils.functional import cached_property
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import PageViewRestriction

from app.core.models import (
    BasePage,
    BasePageWithRequiredIntro,
    ContentWarningMixin,
    HeroImageMixin,
    PublishedDateMixin,
)
from app.core.serializers.pages import DefaultPageSerializer
from app.people.models import AuthorPageMixin, ExternalAuthorMixin, PersonPage

from .blocks import BlogPostPageStreamBlock
from .serializers import BlogPostAuthorsSerializer


def get_blog_post_author_counts(queryset, limit=None):
    author_ids = {
        author_id
        for author_id, live in queryset.order_by()
        .values_list("author_tags__author", "author_tags__author__live")
        .distinct()
        if author_id is not None and live
    }
    if not author_ids:
        return []

    # A separate join preserves counts when the post queryset is filtered by author.
    counts = (
        queryset.filter(author_tags__author_id__in=author_ids)
        .order_by()
        .values("author_tags__author_id")
        .annotate(posts=Count("pk"))
        .order_by("-posts", "author_tags__author_id")
    )
    if limit is not None:
        counts = counts[:limit]
    counts = list(counts)
    authors = (
        PersonPage.objects.filter(
            pk__in=[row["author_tags__author_id"] for row in counts]
        )
        .select_related("image", "teaser_image")
        .prefetch_related("roles__role")
        .in_bulk()
    )
    return [
        {"author": authors[row["author_tags__author_id"]], "posts": row["posts"]}
        for row in counts
    ]


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
        return BlogFeedsPage.objects.all().live().public().first()

    @cached_property
    def top_blogs(self):
        """
        Returns top-level blogs.
        """
        queryset = (
            BlogPage.objects.all()
            .live()
            .public()
            .select_related("teaser_image")
            .order_by("title")
        )
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.all().select_related("page")
        ]
        for restricted_page in restricted_pages:
            queryset = queryset.not_descendant_of(restricted_page, inclusive=True)

        for blog in queryset:
            # Ignore all "sub-blogs" (BlogPages which are children of other BlogPages)
            queryset = queryset.not_descendant_of(blog, inclusive=False)

        return queryset

    @cached_property
    def blog_posts_count(self):
        """
        Returns blog post counts aggregated by year and month.
        Replicates the logic from blog_posts/count/ endpoint.
        """
        queryset = BlogPostPage.objects.all().live().public()

        monthly_counts = (
            queryset.annotate(
                year=ExtractYear("published_date"),
                month=ExtractMonth("published_date"),
            )
            .values("year", "month")
            .annotate(posts=Count("id"))
            .order_by("year", "month")
        )

        years_dict = {}
        for row in monthly_counts:
            year, month, count = row["year"], row["month"], row["posts"]
            acc = years_dict.setdefault(year, {"year": year, "months": [], "posts": 0})
            acc["months"].append({"month": month, "posts": count})
            acc["posts"] += count

        return list(years_dict.values())

    @cached_property
    def blog_posts_authors(self):
        """
        Returns blog post authors with their post counts.
        Replicates the logic from blog_posts/authors/ endpoint.
        Limited to top 12 authors.
        """
        queryset = BlogPostPage.objects.all().live().public()
        return get_blog_post_author_counts(queryset, limit=12)

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("blogs_feeds_page", serializer=DefaultPageSerializer()),
        APIField("top_blogs", serializer=DefaultPageSerializer(many=True)),
        APIField("blog_posts_count"),
        APIField("blog_posts_authors", serializer=BlogPostAuthorsSerializer()),
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

    @cached_property
    def blogs_feeds_page(self):
        """
        Returns the blogs feeds page.
        """
        return BlogFeedsPage.objects.all().live().public().first()

    @cached_property
    def child_blogs(self):
        """
        Returns child BlogPages of this page with post counts.
        """
        queryset = (
            BlogPage.objects.child_of(self)
            .live()
            .public()
            .select_related("teaser_image")
            .order_by("title")
        )
        return queryset

    @cached_property
    def top_blogs(self):
        """
        Returns "top-most" level blogs.
        """
        blog_index = (
            BlogIndexPage.objects.all()
            .live()
            .public()
            .select_related("teaser_image")
            .first()
        )
        if not blog_index:
            return None

        queryset = (
            BlogPage.objects.child_of(blog_index)
            .live()
            .public()
            .select_related("teaser_image")
            .order_by("title")
        )
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.all().select_related("page")
        ]
        for restricted_page in restricted_pages:
            queryset = queryset.not_descendant_of(restricted_page, inclusive=True)

        for blog in queryset:
            # Ignore all "sub-blogs" (BlogPages which are children of other BlogPages)
            queryset = queryset.not_descendant_of(blog, inclusive=False)

        return [blog_index] + list(queryset)

    @cached_property
    def blog_posts_count(self):
        """
        Returns blog post counts aggregated by year and month for this blog's posts.
        """
        queryset = BlogPostPage.objects.descendant_of(self).live().public()

        monthly_counts = (
            queryset.annotate(
                year=ExtractYear("published_date"),
                month=ExtractMonth("published_date"),
            )
            .values("year", "month")
            .annotate(posts=Count("id"))
            .order_by("year", "month")
        )

        years_dict = {}
        for row in monthly_counts:
            year, month, count = row["year"], row["month"], row["posts"]
            acc = years_dict.setdefault(year, {"year": year, "months": [], "posts": 0})
            acc["months"].append({"month": month, "posts": count})
            acc["posts"] += count

        return list(years_dict.values())

    @cached_property
    def blog_posts_authors(self):
        """
        Returns blog post authors with their post counts for this blog's posts.
        Limited to top 12 authors.
        """
        queryset = BlogPostPage.objects.descendant_of(self).live().public()
        return get_blog_post_author_counts(queryset, limit=12)

    content_panels = (
        BasePageWithRequiredIntro.content_panels + HeroImageMixin.content_panels
    )

    promote_panels = BasePageWithRequiredIntro.promote_panels + [
        FieldPanel("custom_type_label"),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + [
            APIField("custom_type_label"),
            APIField("blogs_feeds_page", serializer=DefaultPageSerializer()),
            APIField("child_blogs", serializer=DefaultPageSerializer(many=True)),
            APIField("top_blogs", serializer=DefaultPageSerializer(many=True)),
            APIField("blog_posts_count"),
            APIField("blog_posts_authors", serializer=BlogPostAuthorsSerializer()),
        ]
    )


def prefetch_top_level_blogs(pages):
    posts = [page for page in pages if isinstance(page, BlogPostPage)]
    if not posts:
        return

    # Wagtail paths consist of fixed-width segments, one per ancestor.
    ancestor_paths = {
        post.path[:length]
        for post in posts
        for length in range(post.steplen, len(post.path), post.steplen)
    }
    blogs = {
        blog.path: blog for blog in BlogPage.objects.filter(path__in=ancestor_paths)
    }
    for post in posts:
        post._top_level_blog = None
        for length in range(post.steplen, len(post.path), post.steplen):
            if blog := blogs.get(post.path[:length]):
                post._top_level_blog = blog
                break


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
    def _top_level_blog(self):
        ancestor = self.get_ancestors().type(BlogPage).first()
        return ancestor.specific if ancestor else None

    @cached_property
    def type_label(self) -> str:
        """
        Overrides the type_label method from BasePage, to return the correct
        type label for the blog post page.
        """
        top_level = self._top_level_blog
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
        return BlogIndexPage.objects.all().live().public().first()

    @cached_property
    def blogs(self):
        """
        Returns the top-level blogs that are not descendants of other blogs.
        """
        all_blogs = BlogPage.objects.all().live().public()
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
