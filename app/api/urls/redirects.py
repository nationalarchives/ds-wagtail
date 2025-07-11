from django.db.models import Q
from wagtail.api.v2.utils import BadRequestError
from wagtail.contrib.redirects.api import RedirectsAPIViewSet as BaseRedirectsAPIViewSet
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Site


class RedirectsAPIViewSet(BaseRedirectsAPIViewSet):
    body_fields = BaseRedirectsAPIViewSet.body_fields + ["is_permanent"]

    listing_default_fields = BaseRedirectsAPIViewSet.listing_default_fields + [
        "is_permanent"
    ]

    known_query_parameters = BaseRedirectsAPIViewSet.known_query_parameters.union(
        ["site"]
    )

    def get_queryset(self):
        request = self.request

        queryset = Redirect.objects.all()

        if "site" in request.GET:
            if ":" in request.GET["site"]:
                (hostname, port) = request.GET["site"].split(":", 1)
                query = {
                    "hostname": hostname,
                    "port": port,
                }
            else:
                query = {
                    "hostname": request.GET["site"],
                }
            try:
                site = Site.objects.get(**query)
            except Site.MultipleObjectsReturned:
                raise BadRequestError(
                    "Your query returned multiple sites. Try adding a port number to your site filter."
                )
        else:
            # Otherwise, find the site from the request
            # site = Site.find_for_request(self.request)

            # Otherwise, use the default site
            site = Site.objects.get(is_default_site=True)

        if site:
            queryset = queryset.filter(Q(site=site) | Q(site=None))

        return queryset
