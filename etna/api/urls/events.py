from etna.api.filters import LocationFilter
from etna.api.urls.pages import CustomPagesAPIViewSet
from etna.whatson.models import EventPage


class EventsAPIViewSet(CustomPagesAPIViewSet):
    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        ["online", "at_tna"]
    )

    filter_backends = [LocationFilter] + CustomPagesAPIViewSet.filter_backends

    model = EventPage
