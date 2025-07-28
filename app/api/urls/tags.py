from django.urls import path
from rest_framework.response import Response
from wagtail.models import Page

from app.api.urls.pages import CustomPagesAPIViewSet
from app.core.serializers import DefaultPageSerializer


class ArticleTagsAPIViewSet(CustomPagesAPIViewSet):
    def tagged_content_view(self, request):
        request_tags = request.query_params.get("tags", None)
        if request_tags:
            tag_slugs = request_tags.split(",")
            tagged_pages = (
                Page.objects.filter(tagged_items__tag__slug__in=tag_slugs)
                .order_by("-first_published_at")
                .distinct()
            )
            return Response(DefaultPageSerializer(tagged_pages, many=True).data)
        return Response(None)

    @classmethod
    def get_urlpatterns(cls):
        """
        This returns a list of URL patterns for the endpoint
        """
        return [
            path(
                "",
                cls.as_view({"get": "tagged_content_view"}),
                name="tagged_content",
            ),
        ]
