import logging

from wagtail.admin.widgets import BaseChooser

from .api import records_client

logger = logging.getLogger(__name__)


class RecordChooser(BaseChooser):
    choose_one_text = "Choose a record"
    choose_another_text = "Choose another record"
    link_to_chosen_text = "Edit this record"
    chooser_modal_url_name = "record_chooser:choose"
    show_edit_link=False
    icon="doc-full"

    def get_instance(self, pk):
        """Fetch related instance on edit form."""
        try:
            return records_client.fetch(iaid=pk)
        except Exception:
            logger.exception(f"Error fetching Record '{pk}'.")
            return None
        
    def get_value_data_from_instance(self, instance):
        return {
            "id": instance.pk,
            self.display_title_key: instance.summary_title,
            "description": instance.listing_description,
            "reference_number": instance.reference_number,
            "edit_item_url": None,
        }
