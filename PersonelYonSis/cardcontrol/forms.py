from django import forms
from .models import Cihaz

class CihazForm(forms.ModelForm):
    class Meta:
        model = Cihaz
        fields = ['kapi_adi', 'ip', 'port', 'seri_no', 'adms_aktif', 'aciklama']
        widgets = {
            'kapi_adi': forms.TextInput(attrs={'class': 'form-control'}),
            'ip': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'seri_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cihaz menüsü → System Info → Serial Number'}),
            'adms_aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

