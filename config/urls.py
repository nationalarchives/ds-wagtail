from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.urls import include, path, re_path
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.utils.urlpatterns import decorate_urlpatterns

from app.api.urls import api_router

handler404 = "app.errors.views.custom_404_error_view"
handler500 = "app.errors.views.custom_500_error_view"
handler503 = "app.errors.views.custom_503_error_view"


def redirect_to_live_site(request):
    if url_has_allowed_host_and_scheme(
        request.path, allowed_hosts=["www.nationalarchives.gov.uk"]
    ):
        new_url = urljoin("https://www.nationalarchives.gov.uk", request.path)
        return HttpResponsePermanentRedirect(new_url)
    return HttpResponsePermanentRedirect("https://www.nationalarchives.gov.uk")


# Redirect URLs from the beta subdomain to the main domain.
redirect_urls = [
    path("", redirect_to_live_site),
    re_path(r"^explore-the-collection/.*$", redirect_to_live_site),
    re_path(r"^people/.*$", redirect_to_live_site),
]

# Public URLs that are meant to be cached.
public_urls = []

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    public_urls += staticfiles_urlpatterns()
    public_urls += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Private URLs that are not meant to be cached.
private_urls = [
    path("healthcheck/", include("app.healthcheck.urls")),
    path("api/v2/", api_router.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]

# Update private URLs to use the "never cache" cache settings.
private_urls = decorate_urlpatterns(private_urls, never_cache)

# Join private and public URLs.
urlpatterns = (
    private_urls + redirect_urls + public_urls + [path("", include(wagtail_urls))]
)

if apps.is_installed("debug_toolbar"):
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns
