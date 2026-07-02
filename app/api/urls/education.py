from django.db.models import Q
from django.utils.timezone import localdate
from wagtail.api.v2.views import path

from app.api.filters import (
    EducationTaxonomyFilter,
    SessionLocationFilter,
)
from app.api.urls.pages import CustomPagesAPIViewSet
from app.education.models import EducationSessionPage, TeachingResourcePage


class EducationResourcesAPIViewSet(CustomPagesAPIViewSet):
    model = TeachingResourcePage
    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        ["key_stage", "time_period", "theme"]
    )

    filter_backends = [
        EducationTaxonomyFilter,
    ] + CustomPagesAPIViewSet.filter_backends

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
        ]


class EducationSessionsAPIViewSet(CustomPagesAPIViewSet):
    model = EducationSessionPage
    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        ["key_stage", "time_period", "theme", "location"]
    )

    filter_backends = [
        EducationTaxonomyFilter,
        SessionLocationFilter,
    ] + CustomPagesAPIViewSet.filter_backends

    def get_queryset(self):
        queryset = super().get_queryset()
        today = localdate()
        return queryset.filter(
            Q(start_date__gte=today)
            | Q(end_date__gte=today)
            | Q(start_date__isnull=True, end_date__isnull=True)
        )

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
        ]
