from django.conf import settings
from django.templatetags.static import static
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from .admin_views import (
    block_usage_report_view,
    invalidate_tree_explorer_cache,
    tree_explorer_view,
)
from .models.partner_logos import partner_logo_chooserviewset, partner_logo_modelviewset


@hooks.register("insert_global_admin_css")
def global_admin_css():
    static = """
        .sidebar-menu-item--active,
        .sidebar-menu-item__link:focus,
        .sidebar-menu-item__link:hover {
            text-shadow: none;
        }
    """
    if settings.ENVIRONMENT_NAME == "production":
        environment_colours = """
        :root {
            --w-color-surface-menus: #8f3415;
            --w-color-surface-menu-item-active: #6b2710;
        }"""
        return f"<style>{static} {environment_colours}</style>"
    if settings.ENVIRONMENT_NAME == "staging":
        environment_colours = """
        :root {
            --w-color-surface-menus: #323334;
            --w-color-surface-menu-item-active: #262627;
        }"""
        return f"<style>{static} {environment_colours}</style>"
    if settings.ENVIRONMENT_NAME == "develop":
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


@hooks.register("insert_editor_js")
def insert_editor_js():
    return f'<script src="{static("core/js/full_url_preview.js")}"></script>'


@hooks.register("register_admin_urls")
def register_tree_explorer_admin_urls():
    return [
        path(
            "tree-explorer/",
            tree_explorer_view,
            name="tree_explorer",
        ),
        path(
            "reports/block-usage/",
            block_usage_report_view,
            name="block_usage_report",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_tree_explorer_menu_item():
    return MenuItem(
        "Site tree",
        reverse("tree_explorer"),
        icon_name="list-ul",
        order=150,
    )


@hooks.register("register_admin_menu_item")
def register_block_usage_report_menu_item():
    return MenuItem(
        "Block usage",
        reverse("block_usage_report"),
        icon_name="terminal",
        order=160,
    )


hooks.register("after_create_page")(invalidate_tree_explorer_cache)
hooks.register("after_edit_page")(invalidate_tree_explorer_cache)
hooks.register("after_delete_page")(invalidate_tree_explorer_cache)
hooks.register("after_move_page")(invalidate_tree_explorer_cache)
hooks.register("after_copy_page")(invalidate_tree_explorer_cache)
hooks.register("after_publish_page")(invalidate_tree_explorer_cache)
hooks.register("after_unpublish_page")(invalidate_tree_explorer_cache)
