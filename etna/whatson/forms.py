from wagtail.admin.forms import WagtailAdminPageForm


class EventPageForm(WagtailAdminPageForm):
    """
    Overriding the base form class on EventPages to allow for 'required' fields
    that do not impact the function of the page. This allows for a non-required field
    in the database, but a required field in the front-end, so that the fields cannot be
    blank. This will satisfy test cases and will be used for the API integration.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["lead_image"].required = True
        self.fields["event_type"].required = True
        self.fields["venue_type"].required = True
        self.fields["event_type"].required = True
