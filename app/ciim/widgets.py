from wagtail.admin.widgets import BaseChooser

from .client import CIIMClient


class BaseRecordChooserWidget(BaseChooser):
    """
    Widget that extends Wagtail's BaseChooser widget
    for use on choosers that query the CIIM API.
    """

    def get_instance(self, value):
        if value is None:
            return None
        elif isinstance(value, dict):
            return value
        else:
            params = {
                "id": value,
            }
            client = CIIMClient(params=params)
            return client.get_record_instance()

    def get_value_data_from_instance(self, instance):
        return {
            "id": instance.get("iaid"),
            "title": f"{instance.get("summaryTitle")} ({instance.get("iaid")})",
        }

    chooser_modal_url_name = "record_chooser:choose"
