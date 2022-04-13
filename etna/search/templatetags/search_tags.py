import types

from typing import Union

from django import forms, template
from django.core.exceptions import ValidationError
from django.forms.boundfield import BoundField
from django.utils.crypto import get_random_string

import bleach

register = template.Library()


@register.simple_tag
def bucket_count(api_response, bucket_name: str) -> int:
    """Output a facet count for a given bucket."""
    try:
        buckets = api_response["aggregations"]["group"]["buckets"]
    except KeyError:
        return 0

    return next(iter(a["doc_count"] for a in buckets if a["key"] == bucket_name), 0)


@register.filter
def record_detail(record: dict, key: str) -> str:
    """Fetch an item from a record's details template.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """
    try:
        return record["_source"]["@template"]["details"][key]
    except KeyError:
        return ""


@register.filter
def record_highlight(record: dict, key: str) -> str:
    """Fetch an item from a an interpretive records source object.

    Django templates don't allow access to keys or attributes prefixed with @

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """

    try:
        highlight = record["highlight"][f"@template.details.{key}"]
    except KeyError:
        return ""

    if isinstance(highlight, (list, tuple)):
        try:
            return highlight[0]
        except IndexError:
            return ""
    else:
        return highlight


@register.filter
def interpretive_detail(record: dict, key: str) -> str:
    """Fetch an item from a an interpretive records source object.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """

    try:
        detail = record["_source"]["source"][key]
    except KeyError:
        return ""

    if isinstance(detail, (list, tuple)):
        try:
            return detail[0]
        except IndexError:
            return ""
    else:
        return detail


@register.filter
def interpretive_url(record: dict) -> str:
    """Fetch a source Url from an interpretive record template.

    Django templates don't allow access to keys or attributes prefixed with @

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """

    try:
        return record["_source"]["@template"]["details"]["sourceUrl"]
    except KeyError:
        return ""


@register.filter
def record_score(record) -> str:
    """Output a record's score.

    Django templates don't allow access to keys or attributes prefixed with _

    https://docs.djangoproject.com/en/4.0/ref/templates/language/#variables
    """
    return record.get("_score")


@register.simple_tag(takes_context=True)
def query_string_include(context, key: str, value: Union[str, int]) -> str:
    """Add key, value to current query string."""

    request = context["request"]

    query_dict = request.GET.copy()
    query_dict[key] = value

    return query_dict.urlencode()


@register.simple_tag(takes_context=True)
def query_string_exclude(context, key: str, value: Union[str, int]) -> str:
    """Remove matching entry from current query string."""

    request = context["request"]

    query_dict = request.GET.copy()
    items = query_dict.getlist(key, [])
    query_dict.setlist(key, [i for i in items if i != str(value)])

    return query_dict.urlencode()


@register.simple_tag(takes_context=True)
def strip_html_with_exceptions(context, raw_html: str, *exclusions: str):
    print(list(exclusions))
    return bleach.clean(raw_html, tags=list(exclusions), strip=True)


class RepeatableBoundField(BoundField):
    """
    A custom BoundField class that applies a 'suffix' to automatically
    generated html element IDs, allowing the same form to be rendered
    multiple times without field ID clashes.
    """

    @property
    def auto_id(self):
        return super().auto_id + getattr(self.form, "_field_id_suffix", "")

    @property
    def is_hidden(self):
        if hasattr(self.form, "_visible_field_names"):
            return self.name not in self.form._visible_field_names
        return self.field.widget.is_hidden

    def _has_changed(self):
        field = self.field
        if field.show_hidden_initial:
            hidden_widget = field.hidden_widget()
            initial_value = self.form._widget_data_value(
                hidden_widget,
                self.html_initial_name,
            )
            try:
                initial_value = field.to_python(initial_value)
            except ValidationError:
                # Always assume data has changed if validation fails.
                return True
        else:
            initial_value = self.initial
        return field.has_changed(initial_value, self.data)

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        if widget is None:
            if hasattr(self.form, "_visible_field_names"):
                if self.name in self.form._visible_field_names:
                    widget = self.field.widget
                    if isinstance(widget, forms.HiddenInput):
                        widget = self.field.__class__.widget
                else:
                    widget = self.field.hidden_widget
        if not isinstance(widget, forms.Widget):
            widget = widget()
        if self.is_hidden and not self._has_changed():
            return ""
        return super().as_widget(widget, attrs, only_initial)


def patch_form_fields(form):
    """
    Patches Field.get_bound_field() for all of the form's fields, so that they
    return ``RepeatableBoundField`` instances.
    """

    def replacement_method(self, form, field_name):
        return RepeatableBoundField(form, self, field_name)

    for field in form.fields.values():
        field.get_bound_field = types.MethodType(replacement_method, field)


@register.simple_tag()
def prepare_form_for_partial_render(form, *visible_field_names, field_id_suffix=None):
    # Set form attributes to be picked up by RepeatableBoundField
    form._field_id_suffix = "_" + (
        field_id_suffix if field_id_suffix else get_random_string(3)
    )
    form._visible_field_names = visible_field_names
    # In case form fields have not been patched already
    patch_form_fields(form)
    return ""


@register.simple_tag()
def prepare_form_for_full_render(form):
    # Unset custom attributes so that RepeatableBoundFields render as normal
    form.__dict__.pop("_field_id_suffix", None)
    form.__dict__.pop("_visible_field_names", None)
    # In case form fields have not been patched already
    patch_form_fields(form)
    return ""
