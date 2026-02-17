from django import forms
from .models import Cihaz

class CihazForm(forms.ModelForm):
    class Meta:
        model = Cihaz
        fields = ['kapi_adi', 'ip', 'port', 'aciklama']
        widgets = {
            'kapi_adi': forms.TextInput(attrs={'class': 'form-control'}),
            'ip': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
