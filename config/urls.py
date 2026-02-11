from urllib.parse import urljoin

from app.api.urls import api_router
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponsePermanentRedirect
from django.urls import include, path
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.utils.urlpatterns import decorate_urlpatterns


def redirect_to_live_site(request):
    if url_has_allowed_host_and_scheme(
        request.path, allowed_hosts=["www.nationalarchives.gov.uk"]
    ):
        new_url = urljoin("https://www.nationalarchives.gov.uk", request.path)
        return HttpResponsePermanentRedirect(new_url)
    return HttpResponsePermanentRedirect("https://www.nationalarchives.gov.uk")


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
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("wagtail-documents/", include(wagtaildocs_urls)),
]

# Update private URLs to use the "never cache" cache settings.
private_urls = decorate_urlpatterns(private_urls, never_cache)

# Join private and public URLs.
urlpatterns = (
    private_urls
    + public_urls
    + [
        path("", include(wagtail_urls)),
    ]
)

if apps.is_installed("debug_toolbar"):
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns
