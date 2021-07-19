from django import forms
from django.utils.functional import cached_property

from wagtail.core.blocks import ChooserBlock

from ..ciim.exceptions import KongError


class KongModelChoiceField(forms.ModelChoiceField):
    # def validate(self, value):
        # import ipdb; ipdb.set_trace()
        # return True

    # def valid_value(self, value):
        # import ipdb; ipdb.set_trace()
        # return True

    # def run_validators(self, value):
        # import ipdb; ipdb.set_trace()
        # ...

    def prepare_value(self, value):
        if value is None:
            return 

        return value.iaid


class RecordChooserBlock(ChooserBlock):
    @cached_property
    def field(self):
        return KongModelChoiceField(
            queryset=self.target_model.objects.all(),
            widget=self.widget,
            required=self._required,
            validators=self._validators,
            help_text=self._help_text,
        )

    @cached_property
    def target_model(self):
        from .models import RecordPage

        return RecordPage

    @cached_property
    def widget(self):
        from .widgets import RecordChooser

        return RecordChooser()

    def get_form_state(self, value):
        return self.widget.get_value_data(value)

    def get_prep_value(self, value):
        # the native value (a model instance or None) should serialise to a PK or None
        if value is None:
            return None
        else:
            return value.iaid

    def bulk_to_python(self, values):
        """Return the model instances for the given list of primary keys.
        The instances must be returned in the same order as the values and keep None values.
        """
        return self.target_model.search.get_multiple(iaid=values)

    def clean(self, value):
        # ChooserBlock works natively with model instances as its 'value' type (because that's what you
        # want to work with when doing front-end templating), but ModelChoiceField.clean expects an ID
        # as the input value (and returns a model instance as the result). We don't want to bypass
        # ModelChoiceField.clean entirely (it might be doing relevant validation, such as checking page
        # type) so we convert our instance back to an ID here. It means we have a wasted round-trip to
        # the database when ModelChoiceField.clean promptly does its own lookup, but there's no easy way
        # around that...
        if isinstance(value, self.target_model):
            return value
        return super().clean(value)

    def to_python(self, pk):
        """Fetch related instance on edit form."""
        try:
            return self.target_model.search.get(iaid=pk)
        except KongError:
            # If there's a connection issue with Kong, return a stub RecordPage
            # so we have something to render on the ResultsPage edit form.
            return RecordPage(iaid=pk)

    def value_from_form(self, value):
        # ModelChoiceField sometimes returns an ID, and sometimes an instance; we want the instance
        if value is None or isinstance(value, self.target_model):
            return value

        try:
            return self.target_model.search.get(iaid=value)
        except KongError:
            # If there's a connection issue with Kong, return a stub RecordPage
            # so we have something to render on the ResultsPage edit form.
            return RecordPage(iaid=value)

    def value_for_form(self, value):
        return value

    class Meta:
        icon = "fa-archive"
