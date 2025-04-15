from etna.whatson.models import EventPage

from ..filters import FilterDateFromToSessionStart
from .pages import CustomPagesAPIViewSet


class EventPagesAPIViewSet(CustomPagesAPIViewSet):
    filter_backends = [
        FilterDateFromToSessionStart
    ] + CustomPagesAPIViewSet.filter_backends

    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        [
            "to",
            "from",
        ]
    )

    model = EventPage
