from django.urls import path
from rest_framework.response import Response
from wagtail.models import PageViewRestriction

from app.api.urls.pages import CustomPagesAPIViewSet
from app.blog.models import BlogIndexPage, BlogPage, BlogPostPage
from app.core.serializers.pages import DefaultPageSerializer


class BlogsAPIViewSet(CustomPagesAPIViewSet):
    model = BlogPage

    def top_level_blogs_list_view(self, request):
        queryset = self.get_queryset()
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.all().select_related("page")
            if not restriction.accept_request(self.request)
        ]
        for restricted_page in restricted_pages:
            queryset = queryset.not_descendant_of(restricted_page, inclusive=True)
        blog_post_counts = {}
        for blog in queryset:
            # Ignore all "sub-blogs" (BlogPages which are children of other BlogPages)
            queryset = queryset.not_descendant_of(blog, inclusive=False)
            blog_posts = BlogPostPage.objects.all().live().descendant_of(blog).count()
            blog_post_counts[blog.id] = blog_posts
        serializer = DefaultPageSerializer(
            queryset, required_api_fields=["custom_type_label"], many=True
        )
        blogs = sorted(serializer.data, key=lambda x: x["title"])
        blogs = [blog | {"posts": blog_post_counts[blog["id"]]} for blog in blogs]
        top_level_queryset = BlogIndexPage.objects.all().live()
        top_level = DefaultPageSerializer(top_level_queryset, many=True)
        blogs = top_level.data + blogs
        return Response(blogs)

    def blog_index_view(self, request):
        queryset = BlogIndexPage.objects.all().live()
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
