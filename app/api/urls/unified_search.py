from itertools import zip_longest

from django.conf import settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from wagtail.models import Page, PageViewRestriction
from wagtail.search.backends import get_search_backend

from app.api.permissions import IsAPITokenAuthenticated
from app.search.models import ExternalApplicationPage


def _serialize_wagtail_page(page):
    specific_page = page.specific
    return {
        "id": page.pk,
        "title": page.title,
        "short_title": page.title,
        "url": page.url,
        "full_url": page.full_url,
        "type": "wagtail_page",
        "type_label": specific_page._meta.verbose_name.title(),
        "teaser_text": page.search_description,
        "teaser_image": None,
        "first_published_at": page.first_published_at,
        "last_published_at": page.last_published_at,
    }


def _serialize_external_application_page(page):
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


class UnifiedSearchAPIViewSet(GenericViewSet):
    if settings.WAGTAILAPI_AUTHENTICATION:
        permission_classes = (IsAPITokenAuthenticated,)

    def listing_view(self, request):
        search_query = (request.GET.get("search") or "").strip()
        if not search_query:
            return Response({"count": 0, "results": []})

        limit = int(request.GET.get("limit", 20))
        if limit < 1:
            limit = 1
        if limit > 100:
            limit = 100

        page_queryset = Page.objects.live().public()
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.all().select_related("page")
        ]
        for restricted_page in restricted_pages:
            page_queryset = page_queryset.not_descendant_of(restricted_page, inclusive=True)

        external_queryset = ExternalApplicationPage.objects.filter(
            application__is_active=True
        ).select_related("application")

        backend = get_search_backend()
        page_results = list(backend.search(search_query, page_queryset)[:limit])
        external_results = list(backend.search(search_query, external_queryset)[:limit])

        merged_results = []
        for page_result, external_result in zip_longest(page_results, external_results):
            if page_result is not None:
                merged_results.append(_serialize_wagtail_page(page_result))
            if external_result is not None:
                merged_results.append(
                    _serialize_external_application_page(external_result)
                )

            if len(merged_results) >= limit:
                break

        return Response({"count": len(merged_results), "results": merged_results})

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
        ]