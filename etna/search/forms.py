from django import forms


class SearchForm(forms.Form):
    keyword = forms.CharField(label="Search here", required=False)
    group = forms.ChoiceField(
        label="bucket",
        choices=[
            ("group:tna", "TNA"),
            ("group:nonTna", "NonTNA"),
            ("group:creator", "Creator"),
            ("group:archive", "Archive"),
        ],
        required=False,
    )

    def clean(self):
        """Collect selected filters to pass to the client in view."""
        cleaned_data = super().clean()

        cleaned_data["filter_aggregations"] = [cleaned_data.get("group")]

        return cleaned_data
