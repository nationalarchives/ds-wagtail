from django import forms


class SearchForm(forms.Form):
    search_text = forms.CharField(label="search here", required=True)
