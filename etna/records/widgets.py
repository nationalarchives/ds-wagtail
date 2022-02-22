from generic_chooser.widgets import AdminChooser

from ..ciim.exceptions import APIManagerException, KongAPIError
from .models import Record


class RecordChooser(AdminChooser):
    choose_one_text = "Choose a record"
    choose_another_text = "Choose another record"
    link_to_chosen_text = "Edit this record"
    choose_modal_url_name = "record_chooser:choose"

    def get_value_data(self, value):
        if isinstance(value, Record):
            return {
                "value": value.iaid,
                "title": self.get_title(value),
                "edit_item_url": self.get_edit_item_url(value),
            }

        # If value isn't a Record instance, it's an iaid that can be directly
        # output in the form field.
        return {
            "value": value,
            "title": "",
            "edit_item_url": "",
        }

    def get_instance(self, pk):
        """Fetch related instance on edit form."""
        try:
            return Record.api.fetch(iaid=pk)
        except (KongAPIError, APIManagerException):
            # If there's a connection issue with Kong, return a stub Record
            # so we have something to render on the ResultsPage edit form.
            return Record(iaid=pk, title="", reference_number="")
