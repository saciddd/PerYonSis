# forms.py
from django import forms
from .models import Mesai_Tanimlari

class MesaiTanimForm(forms.ModelForm):
    class Meta:
        model = Mesai_Tanimlari
        fields = '__all__'
        widgets = {
            'Saat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08:00 16:00'}),
            'CKYS_BTF_Karsiligi': forms.TextInput(attrs={'class': 'form-control'}),
            'AraDinlenme': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'Renk': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'GunduzMesaisi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'AksamMesaisi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'GeceMesaisi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'IseGeldi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'SonrakiGuneSarkiyor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'GecerliMesai': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
