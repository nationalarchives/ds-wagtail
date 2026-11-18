from app.api.filters import RecordFilter
from app.api.urls.pages import CustomPagesAPIViewSet
from app.research.models import ResearchGuide


class ResearchGuidesAPIViewSet(CustomPagesAPIViewSet):
    model = ResearchGuide
    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        ["record", "ancestor"]
    )

    filter_backends = [RecordFilter] + CustomPagesAPIViewSet.filter_backends
