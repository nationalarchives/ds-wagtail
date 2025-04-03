from .client import CIIMClient
from django.conf import settings
from wagtail.admin.widgets import BaseChooser


class BaseRecordChooserWidget(BaseChooser):
    def get_instance(self, value):
        if value is None:
            return None
        elif isinstance(value, dict):
            return value
        else:
            params = {
                "id": value,
            }
            client = CIIMClient(api_url=settings.CLIENT_BASE_URL, params=params)
            result = client.get_record_instance()
            result = result.get("data", [])[0].get("@template", {}).get("details", {})
            return result

    def get_value_data_from_instance(self, instance):
        return {
            "id": instance["iaid"],
            "title": f"{instance["summaryTitle"]} ({instance["iaid"]})",
        }

    chooser_modal_url_name = "record_chooser:choose"
