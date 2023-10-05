from django import forms

class EventFilterForm(forms.Form):
    date = forms.DateField(label="Choose a date", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    category = forms.CheckboxSelectMultiple()
    online = forms.BooleanField(label="Online", required=False)
    family_friendly = forms.BooleanField(label="Family friendly", required=False)
    