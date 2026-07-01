from app.api.urls.pages import CustomPagesAPIViewSet
from app.education.models import EducationSessionPage, TeachingResourcePage

class EducationResourcesAPIViewSet(CustomPagesAPIViewSet):
    model = TeachingResourcePage
    known_query_parameters = CustomPagesAPIViewSet.known_query_parameters.union(
        ["key_stage", "time_period", "theme"]
    )

#copied from events.py to replace with appropriate filters
    # filter_backends = [
    #     # LocationFilter,
    #     # EventDateFilter,
    # ] + CustomPagesAPIViewSet.filter_backends

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

#copied from events.py to replace with appropriate filters
    # filter_backends = [
    #     # LocationFilter,
    #     # EventDateFilter,
    # ] + CustomPagesAPIViewSet.filter_backends

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
        ]