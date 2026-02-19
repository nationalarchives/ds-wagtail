from app.api.filters import AuthorFilter, PublishedDateFilter
from app.api.urls.pages import CustomPagesAPIViewSet
from app.blog.models import BlogPostPage
from app.core.serializers.pages import DefaultPageSerializer
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.urls import path
from rest_framework.response import Response


class BlogPostsAPIViewSet(CustomPagesAPIViewSet):
    filter_backends = [
        PublishedDateFilter,
        AuthorFilter,
    ] + CustomPagesAPIViewSet.filter_backends  # Needs to be last as it includes SearchFilter which needs to be last
    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        [
            "year",
            "month",
            "day",
            "author",
        ]
    )
    model = BlogPostPage

    def count_view(self, request):
        queryset = self.get_queryset().public()
        self.check_query_parameters(queryset)
        queryset = self.filter_queryset(queryset).public()

        # Add computed fields/aggregates
        monthly_counts = (
            queryset.annotate(
                year=ExtractYear("published_date"),
                month=ExtractMonth("published_date"),
            )
            .values("year", "month")
            .annotate(posts=Count("id"))  # Only count how many posts there are once
            .order_by("year", "month")
        )

        years_map = {}
        for row in monthly_counts:
            year, month, count = row["year"], row["month"], row["posts"]
            acc = years_map.setdefault(year, {"year": year, "months": [], "posts": 0})
            acc["months"].append({"month": month, "posts": count})
            acc["posts"] += count

        return Response(list(years_map.values()))

    def author_view(self, request):
        queryset = self.get_queryset().public()
        self.check_query_parameters(queryset)
        queryset = self.filter_queryset(queryset)
        authors = set(
            queryset.values_list("author_tags__author", "author_tags__author__live")
        )
        serializer = DefaultPageSerializer()
        authors_count = []
        for author in authors:
            if author[0] is not None and author[1]:
                author_item = (
                    queryset.filter(author_tags__author=author)
                    .first()
                    .author_tags.filter(author=author)
                    .first()
                    .author
                )
                authors_count.append(
                    {
                        "author": serializer.to_representation(author_item),
                        "posts": queryset.filter(author_tags__author=author).count(),
                    }
                )
        return Response(sorted(authors_count, key=lambda x: x["posts"], reverse=True))

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
            path("count/", cls.as_view({"get": "count_view"}), name="count"),
            path("authors/", cls.as_view({"get": "author_view"}), name="authors"),
        ]
