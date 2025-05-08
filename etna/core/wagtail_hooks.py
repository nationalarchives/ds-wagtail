from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks


@hooks.register("insert_global_admin_css")
def editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">', static("css/wagtail-overrides.css")
    )


@hooks.register("insert_editor_js")
def editor_js():
    return format_html(
        '<script src="{}"></script>',
        static("admin/js/inputLengthIndicators.js"),
    )


@hooks.register("insert_global_admin_js")
def global_admin_js():
    return "<script>window.chooserUrls = {'pageChooser': '/admin/choose-page/','externalLinkChooser': '/admin/choose-external-link/','emailLinkChooser': '/admin/choose-email-link/','phoneLinkChooser': '/admin/choose-phone-link/','anchorLinkChooser': '/admin/choose-anchor-link/',}; </script> <script src='/static/wagtailadmin/js/modal-workflow.js?v=4a9c2a53'></script>"


@hooks.register("insert_global_admin_css")
def global_admin_css():
    static = """
        :root {
            --w-color-surface-menu-item-active: var(--w-color-surface-page);
        }
        @media (prefers-color-scheme: light) {
            :root {
                --w-color-text-label-menus-active: #010101;
            }
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --w-color-text-label-menus-active: #fff;
            }
        }
        .sidebar-menu-item--active,
        .sidebar-menu-item__link:focus,
        .sidebar-menu-item__link:hover {
            text-shadow: none;
        }
        .sidebar-menu-item__link:focus,
        .sidebar-menu-item__link:hover {
            color: #fff;
        }
        .sidebar-menu-item--active .sidebar-menu-item__link:focus,
        .sidebar-menu-item--active .sidebar-menu-item__link:hover {
            color: inherit;
        }
    """
    environment_colours = ""

    if settings.ENVIRONMENT_NAME == "production":
        environment_colours = """
        :root {
            --w-color-surface-menus: #8f3415;
        }"""
    elif settings.ENVIRONMENT_NAME == "staging":
        environment_colours = """
        :root {
            --w-color-surface-menus: #323334;
        }"""
    elif settings.ENVIRONMENT_NAME == "develop":
        environment_colours = """
        :root {
            --w-color-surface-menus: #00623b;
        }"""

    return f"<style>{static} {environment_colours}</style>"


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
