from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import AdminOnlyMenuItem

from .views import beta_testers_report


@hooks.register("register_reports_menu_item")
def register_unpublished_changes_report_menu_item():
    return AdminOnlyMenuItem(
        "Beta testers",
        reverse("beta_testers_report"),
        classname="icon icon-user",
    )


@hooks.register("register_admin_urls")
def register_unpublished_changes_report_url():
    return [
        path(
            "reports/beta-testers/",
            beta_testers_report,
            name="beta_testers_report",
        ),
    ]
