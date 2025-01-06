import logging

from generic_chooser.widgets import AdminChooser

from .api import records_client
from .models import Record

logger = logging.getLogger(__name__)


class RecordChooser(AdminChooser):
    choose_one_text = "Choose a record"
    choose_another_text = "Choose another record"
    link_to_chosen_text = "Edit this record"
    choose_modal_url_name = "record_chooser:choose"

    def get_value_data(self, value):
        # Given a data value (which may be None or an value such as a pk to pass to get_instance),
        # extract the necessary data for rendering the widget with that value.
        # In the case of StreamField (in Wagtail >=2.13), this data will be serialised via
        # telepath https://wagtail.github.io/telepath/ to be rendered client-side, which means it
        # cannot include model instances. Instead, we return the raw values used in rendering -
        # namely: value, title and edit_item_url

        instance = None

        if isinstance(value, Record):
            instance = value
            value = value.iaid
        elif value:
            try:
                instance = self.get_instance(value)
            except Exception:
                logger.exception(
                    f"Error fetching Record '{value}'. Using dummy value."
                )
                return {
                    "value": value,
                    "title": "Record currently unavailable",
                    "edit_item_url": None,
                }

        if instance is None:
            return {
                "value": None,
                "title": "",
                "edit_item_url": None,
            }

        return {
            "value": value,
            "title": self.get_title(instance),
            "edit_item_url": self.get_edit_item_url(instance),
        }

    def get_instance(self, pk):
        """Fetch related instance on edit form."""
        return records_client.fetch(iaid=pk)
