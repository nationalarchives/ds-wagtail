from .pages import CustomPagesAPIViewSet
from ..filters import FilterDateFromTo
from etna.whatson.models import EventPage

class EventPagesAPIViewSet(CustomPagesAPIViewSet):
    filter_backends = [
        FilterDateFromTo
    ] + CustomPagesAPIViewSet.filter_backends

    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        [
            "to",
            "from",
        ]
    )

    model = EventPage