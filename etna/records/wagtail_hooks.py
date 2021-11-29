from wagtail.core import hooks

from .views import RecordChooserViewSet


@hooks.register("register_admin_viewset")
def register_record_chooser_viewset():
    return RecordChooserViewSet("record_chooser", url_prefix="record-chooser")


@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        'wagtailfontawesomesvg/solid/star.svg',
        'wagtailfontawesomesvg/solid/archive.svg',
        'wagtailfontawesomesvg/solid/list.svg',
        'wagtailfontawesomesvg/solid/external-link-alt.svg',
        'wagtailfontawesomesvg/solid/play.svg',
        'wagtailfontawesomesvg/solid/paragraph.svg',
        'wagtailfontawesomesvg/solid/heading.svg',
        'wagtailfontawesomesvg/solid/user-circle.svg',
        'wagtailfontawesomesvg/solid/th.svg',
        'wagtailfontawesomesvg/solid/arrow-up.svg',
        'wagtailfontawesomesvg/solid/th-large.svg',
    ]
