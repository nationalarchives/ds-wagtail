from wagtail import hooks

from .views import record_chooser_viewset


@hooks.register("register_admin_viewset")
def register_record_chooser_viewset():
    return record_chooser_viewset
