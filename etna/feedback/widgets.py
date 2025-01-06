from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst
from wagtail.blocks import StreamValue
from wagtail.models import Page, get_page_models


class ResponseSubmitButtonList(forms.RadioSelect):
    template_name = "feedback/widgets/response_submit_button_list.html"
    option_template_name = "feedback/widgets/response_submit_button.html"

    def __init__(self, response_options: StreamValue, attrs=None):
        super().__init__(attrs)
        self.choices = list(
            (option.id, option.value["label"]) for option in response_options
        )
        self.icons = {option.id: option.value["icon"] for option in response_options}
        self.sentiments = {
            option.id: option.value["sentiment"] for option in response_options
        }

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        option.update(
            icon=self.icons[value],
            sentiment=self.sentiments[value],
        )
        return option


class PageTypeChooser(forms.Select):
    @property
    def choices(self):
        items = []
        for model in get_page_models():
            if model is not Page:
                ct = ContentType.objects.get_for_model(model)
                items.append(
                    (
                        ct.id,
                        f"{capfirst(model._meta.app_label)}: {capfirst(model._meta.verbose_name)}",
                    )
                )
        return sorted(items, key=lambda x: x[1])

    @choices.setter
    def choices(self, value):
        # Ignore attempts to set choices
        pass
