from django import forms


class SearchForm(forms.Form):
    keyword = forms.CharField(label="Search here", required=False)
