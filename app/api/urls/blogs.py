from django.db.models import Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.urls import path
from rest_framework.response import Response
from wagtail.models import PageViewRestriction

from app.api.urls.pages import CustomPagesAPIViewSet
from app.blog.models import BlogIndexPage, BlogPage, BlogPostPage
from app.core.serializers.pages import DefaultPageSerializer


class BlogsAPIViewSet(CustomPagesAPIViewSet):
    model = BlogPage

    def top_level_blogs_list_view(self, request):
        queryset = BlogPage.objects.all().live().public().order_by("title")
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.all().select_related("page")
        ]
        for restricted_page in restricted_pages:
            queryset = queryset.not_descendant_of(restricted_page, inclusive=True)
        post_counts = (
            BlogPostPage.objects.live()
            .public()
            .filter(path__startswith=OuterRef("path"))
            .order_by()
            .annotate(count_group=Value(1))
            .values("count_group")
            .annotate(total=Count("pk"))
            .values("total")
        )
        queryset = queryset.annotate(
            listing_post_count=Coalesce(
                Subquery(post_counts, output_field=IntegerField()), Value(0)
            )
        ).select_related("teaser_image")
        blog_post_counts = {}
        for blog in queryset:
            # Ignore all "sub-blogs" (BlogPages which are children of other BlogPages)
            queryset = queryset.not_descendant_of(blog, inclusive=False)
            blog_post_counts[blog.id] = blog.listing_post_count
        serializer = DefaultPageSerializer(
            queryset, required_api_fields=["custom_type_label"], many=True
        )
        blogs = [
            blog | {"posts": blog_post_counts[blog["id"]]} for blog in serializer.data
        ]
        top_level_queryset = (
            BlogIndexPage.objects.all().live().public().select_related("teaser_image")
        )
        top_level = DefaultPageSerializer(top_level_queryset, many=True)
        blogs = top_level.data + blogs
        return Response(blogs)

    def blog_index_view(self, request):
        queryset = (
            BlogIndexPage.objects.all().live().public().select_related("teaser_image")
        )
        blog_index = DefaultPageSerializer(queryset, many=True)
        return Response(blog_index.data[0] if len(blog_index.data) else None)

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path("", cls.as_view({"get": "listing_view"}), name="blogs_list"),
            path(
                "index/",
                cls.as_view({"get": "blog_index_view"}),
                name="blogs_index",
            ),
            path(
                "top/",
                cls.as_view({"get": "top_level_blogs_list_view"}),
                name="top_level_blogs_list",
            ),
        ]
