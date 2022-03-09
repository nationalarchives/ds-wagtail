from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path, register_converter
from django.views.decorators.cache import never_cache

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.utils.urlpatterns import decorate_urlpatterns

from etna.core.cache_control import (
    apply_default_cache_control,
    apply_default_vary_headers,
)
from etna.records import converters
from etna.records import views as records_views
from etna.search import views as search_views

register_converter(converters.ReferenceNumberConverter, "reference_number")
register_converter(converters.IAIDConverter, "iaid")


# Private URLs that are not meant to be cached.
private_urls = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("accounts/", include("allauth.urls")),
    path("documents/", include(wagtaildocs_urls)),
]

# Public URLs that are meant to be cached.
public_urls = [
    path(
        r"catalogue/<iaid:iaid>/",
        login_required(records_views.record_detail_view),
        name="details-page-machine-readable",
    ),
    path(
        r"catalogue/<reference_number:reference_number>/",
        login_required(records_views.record_disambiguation_view),
        name="details-page-human-readable",
    ),
    path(
        "records/image/<path:location>",
        records_views.image_serve,
        name="image-serve",
    ),
    path(
        r"records/images/<iaid:iaid>/<str:sort>/",
        login_required(records_views.image_viewer),
        name="image-viewer",
    ),
    path(
        r"records/images/<iaid:iaid>/",
        login_required(records_views.image_browse),
        name="image-browse",
    ),
    path(
        r"search/catalogue/",
        login_required(search_views.catalogue_search),
        name="search-catalogue",
    ),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    public_urls += staticfiles_urlpatterns()
    public_urls += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Update public URLs to use the "default" cache settings.
public_urls = decorate_urlpatterns(public_urls, apply_default_cache_control)

# Set vary headers for public URLS to instruct cache to serve different version on
# different cookies, different request method (e.g. AJAX) and different protocol
# (http vs https).
public_urls = decorate_urlpatterns(public_urls, apply_default_vary_headers)

# Update private URLs to use the "never cache" cache settings.
private_urls = decorate_urlpatterns(private_urls, never_cache)

# Join private and public URLs.
urlpatterns = (
    private_urls
    + public_urls
    + [
        # Wagtail URLs are added at the end.
        # cache-control is applied to the page models's serve methods
        path("", include(wagtail_urls)),
    ]
)
