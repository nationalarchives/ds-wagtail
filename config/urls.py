from django.apps import apps
from django.conf import settings
from django.urls import include, path
from django.views.decorators.cache import never_cache
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.utils.urlpatterns import decorate_urlpatterns

from etna.api.urls import api_router
from etna.core.cache_control import (
    apply_default_cache_control,
    apply_default_vary_headers,
)
from etna.errors import views as errors_view

handler404 = "etna.errors.views.custom_404_error_view"
handler500 = "etna.errors.views.custom_500_error_view"
handler503 = "etna.errors.views.custom_503_error_view"

# Private URLs that are not meant to be cached.
private_urls = [
    path("healthcheck/", include("etna.healthcheck.urls")),
    path("api/v2/", api_router.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("accounts/", include("allauth.urls")),
    path("documents/", include(wagtaildocs_urls)),
]

# Public URLs that are meant to be cached.
public_urls = []

# TODO: Remove this whole block when the frontend is removed
if settings.DEBUG:
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
