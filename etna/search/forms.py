from django import forms


class SearchForm(forms.Form):
    search_text = forms.CharField(label="search here", required=True)
    bucket = forms.ChoiceField(
        label="bucket", choices=[("nonTna", "Non-TNA"), ("tna", "TNA")]
    )
    sort = forms.ChoiceField(
        label="sort", choices=[("title", "Title"), ("date_created", "Date Created")]
    )
