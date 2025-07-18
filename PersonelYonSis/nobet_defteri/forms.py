from django import forms
from .models import NobetDefteri, NobetOlayKaydi

class NobetDefteriForm(forms.ModelForm):
    class Meta:
        model = NobetDefteri
        fields = ['tarih', 'nobet_turu', 'vardiya', 'aciklama']
        widgets = {
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nobet_turu': forms.Select(attrs={'class': 'form-select'}),
            'vardiya': forms.Select(attrs={'class': 'form-select'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class NobetOlayKaydiForm(forms.ModelForm):
    class Meta:
        model = NobetOlayKaydi
        fields = ['saat', 'konu', 'detay']
        widgets = {
            'saat': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'konu': forms.TextInput(attrs={'class': 'form-control'}),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
