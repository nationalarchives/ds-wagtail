from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, register_converter
from django.views.decorators.cache import never_cache

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.utils.urlpatterns import decorate_urlpatterns

from etna.core.cache_control import (
    apply_default_cache_control,
    apply_default_vary_headers,
)
from etna.core.decorators import setting_controlled_login_required
from etna.errors import views as errors_view
from etna.records import converters
from etna.records import views as records_views
from etna.search import views as search_views

register_converter(converters.ReferenceNumberConverter, "reference_number")
register_converter(converters.IAIDConverter, "iaid")


# Used by /sentry-debug/
def trigger_error(request):
    # Raise a ZeroDivisionError
    return 1 / 0


handler404 = "etna.errors.views.custom_404_error_view"
handler500 = "etna.errors.views.custom_500_error_view"
handler503 = "etna.errors.views.custom_503_error_view"

# Private URLs that are not meant to be cached.
private_urls = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("accounts/", include("allauth.urls")),
    path("documents/", include(wagtaildocs_urls)),
    path("feedback/", include("etna.feedback.urls")),
    path("healthcheck/", include("etna.healthcheck.urls")),
]

if settings.SENTRY_DEBUG_URL_ENABLED:
    # url is toggled via the SENTRY_DEBUG_URL_ENABLED .env var
    private_urls.append(path("sentry-debug/", trigger_error))

# Public URLs that are meant to be cached.
public_urls = [
    path(
        r"catalogue/id/<iaid:iaid>/",
        setting_controlled_login_required(
            records_views.record_detail_view, "RECORD_DETAIL_REQUIRE_LOGIN"
        ),
        name="details-page-machine-readable",
    ),
    path(
        r"catalogue/ref/<reference_number:reference_number>/",
        setting_controlled_login_required(
            records_views.record_disambiguation_view, "RECORD_DETAIL_REQUIRE_LOGIN"
        ),
        name="details-page-human-readable",
    ),
    path(
        "records/image/<path:location>",
        records_views.image_serve,
        name="image-serve",
    ),
    path(
        r"records/images/<iaid:iaid>/<str:sort>/",
        setting_controlled_login_required(
            records_views.image_viewer, "IMAGE_VIEWER_REQUIRE_LOGIN"
        ),
        name="image-viewer",
    ),
    path(
        r"records/images/<iaid:iaid>/",
        setting_controlled_login_required(
            records_views.image_browse, "IMAGE_VIEWER_REQUIRE_LOGIN"
        ),
        name="image-browse",
    ),
    path(
        r"search/",
        setting_controlled_login_required(
            search_views.SearchLandingView.as_view(), "SEARCH_VIEWS_REQUIRE_LOGIN"
        ),
        name="search",
    ),
    path(
        r"search/featured/",
        setting_controlled_login_required(
            search_views.FeaturedSearchView.as_view(), "SEARCH_VIEWS_REQUIRE_LOGIN"
        ),
        name="search-featured",
    ),
    path(
        r"search/catalogue/",
        setting_controlled_login_required(
            search_views.CatalogueSearchView.as_view(), "SEARCH_VIEWS_REQUIRE_LOGIN"
        ),
        name="search-catalogue",
    ),
    path(
        r"search/catalogue/long-filter-chooser/<str:field_name>/",
        setting_controlled_login_required(
            search_views.CatalogueSearchLongFilterView.as_view(),
            "SEARCH_VIEWS_REQUIRE_LOGIN",
        ),
        name="search-catalogue-long-filter-chooser",
    ),
]

if settings.DEBUG or settings.DJANGO_SERVE_STATIC:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    public_urls += staticfiles_urlpatterns()
    public_urls += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    public_urls += [
        path(
            r"404/",
            errors_view.custom_404_error_view,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(r"500/", errors_view.custom_500_error_view),
        path(r"503/", errors_view.custom_503_error_view),
    ]

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

if apps.is_installed("debug_toolbar"):
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns
