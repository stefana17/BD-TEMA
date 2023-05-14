from datetime import date

from django import forms

class ProdusForm(forms.Form):
    pret_produs = forms.DecimalField(required=True, min_value=10, max_value=9999)
    nume_produs = forms.CharField(required=True)
    cantitate_disponibila = forms.DecimalField(required=True, min_value=1, max_value=9999)


class AprovizionareForm(forms.Form):
    data_aprovizionare = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))
    pret_aprovizionare = forms.DecimalField(required=True, min_value=10, max_value=9999)
    cantitate_aprovizionare = forms.DecimalField(required=True,min_value=1, max_value=999)

    def clean_data_aprovizionare(self):
        data_aprovizionare = self.cleaned_data['data_aprovizionare']
        if data_aprovizionare < date.today():
            raise forms.ValidationError("Data de aprovizionare nu poate fi din trecut!")
        return data_aprovizionare

class EditareProdusForm(forms.Form):
    pret_produs = forms.DecimalField(required=True, min_value=10, max_value=9999)
    nume_produs = forms.CharField(required=True)
    cantitate_disponibila = forms.IntegerField(required=False, disabled=True)
