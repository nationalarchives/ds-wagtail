from wagtail import hooks

from .views import RecordChooserViewSet


@hooks.register("register_admin_viewset")
def register_record_chooser_viewset():
    return RecordChooserViewSet("record_chooser", url_prefix="record-chooser")


@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        "wagtailfontawesomesvg/solid/star.svg",
        "wagtailfontawesomesvg/solid/box-archive.svg",
        "wagtailfontawesomesvg/solid/list.svg",
        "wagtailfontawesomesvg/solid/up-right-from-square.svg",
        "wagtailfontawesomesvg/solid/play.svg",
        "wagtailfontawesomesvg/solid/paragraph.svg",
        "wagtailfontawesomesvg/solid/heading.svg",
        "wagtailfontawesomesvg/solid/circle-user.svg",
        "wagtailfontawesomesvg/solid/table-cells.svg",
        "wagtailfontawesomesvg/solid/arrow-up.svg",
        "wagtailfontawesomesvg/solid/table-cells-large.svg",
    ]
