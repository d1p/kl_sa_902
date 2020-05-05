from django import forms


class PayableDetailsSearchForm(forms.Form):
    from_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}),
                                )
    to_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}),
                              )
