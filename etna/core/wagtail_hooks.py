from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html

from wagtail import hooks


@hooks.register("insert_editor_css")
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("css/wagtail-overrides.css")
    )


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        '<script src="{}"></script>', static("admin/js/inputLengthIndicators.js")
    )


@hooks.register("insert_global_admin_css")
def global_admin_css():
    if settings.FEATURE_PLATFORM_ENVIRONMENT_TYPE != "production":
        return "<style> @media (prefers-color-scheme: light) { :root {--w-color-primary: #00623B; --w-color-primary-200: #003c1e;} } @media (prefers-color-scheme: dark) { :root {--w-color-surface-menus: #002510; --w-color-surface-menu-item-active: #001810;} }</style>"
    return ""
