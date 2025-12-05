from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.urls import include, path
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from wagtail import hooks
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.admin.userbar import AccessibilityItem
from wagtail.admin.utils import get_admin_base_url
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.utils.urlpatterns import decorate_urlpatterns

from app.api.urls import api_router

from .views import UserbarView


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
    path("admin/", include(wagtailadmin_urls)),
    path("wagtail-documents/", include(wagtaildocs_urls)),
    path("userbar/", UserbarView.as_view(), name="wagtail_userbar"),
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


class HeadlessAccessibilityItem(AccessibilityItem):
    def get_axe_spec(self, request):
        spec = super().get_axe_spec(request)
        spec["allowedOrigins"] = [
            (
                "https://my.headless.site"  # Replace with your frontend URL
                if self.in_editor
                else get_admin_base_url()
            )
        ]
        return spec


@hooks.register("construct_wagtail_userbar")
def replace_userbar_accessibility_item(request, items, page):
    items[:] = [
        (
            HeadlessAccessibilityItem(in_editor=item.in_editor)
            if isinstance(item, AccessibilityItem)
            else item
        )
        for item in items
    ]


if apps.is_installed("debug_toolbar"):
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns
