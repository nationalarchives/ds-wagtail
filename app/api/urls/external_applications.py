from django.conf import settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from wagtail.search.backends import get_search_backend

from app.api.permissions import IsAPITokenAuthenticated
from app.search.models import ExternalApplicationPage


def _serialize_page(page):
    return {
        "id": page.pk,
        "title": page.title,
        "short_title": page.short_title,
        "url": page.url_path,
        "full_url": page.full_url,
        "type": "external_application",
        "type_label": page.application.type_label,
        "teaser_text": page.description,
        "teaser_image": page.teaser_image,
        "first_published_at": page.application.first_published_at,
        "last_published_at": page.application.last_published_at,
    }


class ExternalApplicationPagesAPIViewSet(GenericViewSet):
    if settings.WAGTAILAPI_AUTHENTICATION:
        permission_classes = (IsAPITokenAuthenticated,)

    def listing_view(self, request):
        queryset = ExternalApplicationPage.objects.filter(
            application__is_active=True
        ).select_related("application")

        search_query = request.GET.get("search")
        if search_query:
            backend = get_search_backend()
            queryset = backend.search(search_query, queryset)

        results = [_serialize_page(page) for page in queryset]
        return Response({"count": len(results), "results": results})

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
        ]
