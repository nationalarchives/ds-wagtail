from wagtail.core import hooks

from .views import RecordChooserViewSet


@hooks.register("register_admin_viewset")
def register_record_chooser_viewset():
    return RecordChooserViewSet("record_chooser", url_prefix="record-chooser")
