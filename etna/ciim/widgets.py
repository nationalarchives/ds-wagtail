import requests
from django.conf import settings
from wagtail.admin.widgets import BaseChooser


class BaseRecordChooserWidget(BaseChooser):
    def get_instance(self, value):
        if value is None:
            return None
        elif isinstance(value, dict):
            return value
        else:
            r = requests.get(f"{settings.CLIENT_BASE_URL}/get?id={value}")
            result = r.json()
            result = result.get("data", [])[0].get("@template", {}).get("details", {})
            return result

    def get_value_data_from_instance(self, instance):
        return {
            "id": instance["iaid"],
            "title": f"{instance["summaryTitle"]} ({instance["iaid"]})",
        }

    chooser_modal_url_name = "record_chooser:choose"
