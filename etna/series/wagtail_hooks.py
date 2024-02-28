from wagtail import hooks

from .admin_views import series_chooser_viewset


@hooks.register("register_admin_viewset")
def register_series_chooser_viewset():
    return series_chooser_viewset
