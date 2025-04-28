from django import forms
from wagtail.admin.forms.choosers import BaseFilterForm


class APIFilterForm(BaseFilterForm):
    q = forms.CharField(
        label="Search",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search"}),
    )

    def filter(self, objects):
        from .views import BaseRecordChooseView

        search_query = self.cleaned_data.get("q")
        if search_query:
            objects = BaseRecordChooseView.get_results_page(self, query=search_query)
        else:
            objects = BaseRecordChooseView.get_results_page(self)
        return objects
