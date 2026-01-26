from rest_framework.permissions import IsAuthenticated
from wagtail.contrib.redirects.api import RedirectsAPIViewSet as BaseRedirectsAPIViewSet
from wagtail.contrib.redirects.models import Redirect

from ..filters import RedirectsSiteFilter


class RedirectsAPIViewSet(BaseRedirectsAPIViewSet):
    permission_classes = (IsAuthenticated,)

    model = Redirect

    body_fields = BaseRedirectsAPIViewSet.body_fields + ["is_permanent"]

    listing_default_fields = BaseRedirectsAPIViewSet.listing_default_fields + [
        "is_permanent"
    ]

    known_query_parameters = BaseRedirectsAPIViewSet.known_query_parameters.union(
        ["site"]
    )

    filter_backends = [
        RedirectsSiteFilter,
    ]
