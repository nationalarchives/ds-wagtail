import requests
from django.conf import settings
from wagtail.admin.views.generic.chooser import (
    ChosenResponseMixin,
    ChosenViewMixin,
)


class RecordChosenViewMixin(ChosenViewMixin):
    def get_object(self, pk):
        r = requests.get(f"{settings.CLIENT_BASE_URL}/get?id={pk}")
        r.raise_for_status()
        result = r.json()
        result = result.get("data", [])[0].get("@template", {}).get("details", {})
        return result


class RecordChosenResponseMixin(ChosenResponseMixin):
    def get_chosen_response_data(self, item):
        return {
            "id": item.get("iaid"),
            "title": f"{item["summaryTitle"]} ({item["iaid"]})",
        }
