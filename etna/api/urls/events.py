from wagtail.api.v2.views import path

from etna.api.filters import EventDateFilter, LocationFilter
from etna.api.urls.pages import CustomPagesAPIViewSet
from etna.whatson.models import EventPage


class EventsAPIViewSet(CustomPagesAPIViewSet):
    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        ["online", "at_tna", "from", "to"]
    )

    filter_backends = [
        LocationFilter,
        EventDateFilter,
    ] + CustomPagesAPIViewSet.filter_backends

    model = EventPage

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
        ]
