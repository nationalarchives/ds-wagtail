from wagtail.contrib.redirects.api import (
    RedirectsAPIViewSet as BaseRedirectsAPIViewSet,
)


class RedirectsAPIViewSet(BaseRedirectsAPIViewSet):
    body_fields = BaseRedirectsAPIViewSet.body_fields + ["is_permanent"]

    listing_default_fields = BaseRedirectsAPIViewSet.listing_default_fields + [
        "is_permanent",
    ]
