from wagtail.models import PageViewRestriction

from app.api.urls.pages import CustomPagesAPIViewSet
from app.core.serializers.pages import DefaultPageSerializer
from app.foi.models import FoiRequestPage


class FreedomOfInformationRequestsAPIViewSet(CustomPagesAPIViewSet):
    model = FoiRequestPage

    def listing_view(self, request):
        queryset = self.get_queryset().public()

        # Exclude pages that the user doesn't have access to
        restricted_pages = [
            restriction.page
            for restriction in PageViewRestriction.objects.all().select_related("page")
            if not restriction.accept_request(self.request)
        ]

        # Exclude the restricted pages and their descendants from the queryset
        for restricted_page in restricted_pages:
            queryset = queryset.not_descendant_of(restricted_page, inclusive=True)

        self.check_query_parameters(queryset)
        queryset = self.filter_queryset(queryset)
        queryset = self.paginate_queryset(queryset)
        serializer = DefaultPageSerializer(
            queryset, required_api_fields=["date", "reference"], many=True
        )
        return self.get_paginated_response(serializer.data)
