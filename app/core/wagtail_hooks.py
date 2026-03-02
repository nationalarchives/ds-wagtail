from django.conf import settings
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.models import PAGE_PERMISSION_CODENAMES, PAGE_PERMISSION_TYPES

from .models.partner_logos import partner_logo_chooserviewset, partner_logo_modelviewset

# see /wagtail/models/pages.py
PAGE_PERMISSION_TYPES.extend(
    [
        ("can_delete_pages", _("Delete"), _("Delete this page")),
        ("can_unpublish_pages", _("Unpublish"), _("Unpublish this page")),
    ]
)
PAGE_PERMISSION_CODENAMES.extend(["can_delete_pages", "can_unpublish_pages"])

try:
    from django.contrib.auth.models import Permission
    from wagtail.users import forms as wagtail_users_forms

    additional_permissions = ["can_delete_pages", "can_unpublish_pages"]
    permissions_queryset = (
        Permission.objects.filter(
            content_type__app_label="wagtailcore",
            content_type__model="page",
            codename__in=list(PAGE_PERMISSION_CODENAMES) + additional_permissions,
        )
        .select_related("content_type")
        .order_by("codename")
    )

    wagtail_users_forms.PagePermissionsForm.base_fields["permissions"].queryset = (
        permissions_queryset
    )
except Exception:
    # safe fallback for migrations
    pass


@hooks.register("insert_global_admin_css")
def global_admin_css():
    static = """
        .sidebar-menu-item--active,
        .sidebar-menu-item__link:focus,
        .sidebar-menu-item__link:hover {
            text-shadow: none;
        }
        /* Until https://github.com/labd/wagtail-2fa/pull/254 is merged and released */
        .field-content > img {
            background: #fff;
        }
    """
    if settings.ENVIRONMENT_NAME == "production":
        environment_colours = """
        :root {
            --w-color-surface-menus: #8f3415;
            --w-color-surface-menu-item-active: #6b2710;
        }"""
        return f"<style>{static} {environment_colours}</style>"
    elif settings.ENVIRONMENT_NAME == "staging":
        environment_colours = """
        :root {
            --w-color-surface-menus: #323334;
            --w-color-surface-menu-item-active: #262627;
        }"""
        return f"<style>{static} {environment_colours}</style>"
    elif settings.ENVIRONMENT_NAME == "develop":
        environment_colours = """
        :root {
            --w-color-surface-menus: #00623b;
            --w-color-surface-menu-item-active: #00492c;
        }"""
        return f"<style>{static} {environment_colours}</style>"
    return f"<style>{static}</style>"


@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        "wagtailfontawesomesvg/solid/star.svg",
        "wagtailfontawesomesvg/solid/box-archive.svg",
        "wagtailfontawesomesvg/solid/indent.svg",
        "wagtailfontawesomesvg/solid/list.svg",
        "wagtailfontawesomesvg/solid/up-right-from-square.svg",
        "wagtailfontawesomesvg/solid/play.svg",
        "wagtailfontawesomesvg/solid/paragraph.svg",
        "wagtailfontawesomesvg/solid/heading.svg",
        "wagtailfontawesomesvg/solid/circle-user.svg",
        "wagtailfontawesomesvg/solid/table-cells.svg",
        "wagtailfontawesomesvg/solid/arrow-up.svg",
        "wagtailfontawesomesvg/solid/table-cells-large.svg",
        "wagtailfontawesomesvg/solid/terminal.svg",
        "wagtailfontawesomesvg/solid/shop.svg",
    ]


@hooks.register("register_admin_viewset")
def register_admin_viewset():
    return partner_logo_modelviewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return partner_logo_chooserviewset
