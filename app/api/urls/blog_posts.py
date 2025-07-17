from django.urls import path
from rest_framework.response import Response

from app.api.filters import AuthorFilter, PublishedDateFilter
from app.api.urls.pages import CustomPagesAPIViewSet
from app.blog.models import BlogPostPage
from app.core.serializers.pages import DefaultPageSerializer


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
        queryset = self.get_queryset()
        self.check_query_parameters(queryset)
        queryset = self.filter_queryset(queryset).public()
        years = set(queryset.values_list("published_date__year", flat=True))
        years_count = [
            {
                "year": year,
                "months": [
                    {
                        "month": month,
                        "posts": queryset.filter(
                            **{
                                "published_date__year": year,
                                "published_date__month": month,
                            }
                        ).count(),
                    }
                    for month in sorted(
                        set(
                            queryset.filter(
                                **{"published_date__year": year}
                            ).values_list("published_date__month", flat=True)
                        )
                    )
                ],
                "posts": queryset.filter(**{"published_date__year": year}).count(),
            }
            for year in sorted(years)
        ]
        return Response(years_count)

    def author_view(self, request):
        queryset = self.get_queryset()
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
