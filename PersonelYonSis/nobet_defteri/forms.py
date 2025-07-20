from django import forms
from .models import NobetDefteri, NobetOlayKaydi
from datetime import date

class NobetDefteriForm(forms.ModelForm):
    class Meta:
        model = NobetDefteri
        fields = ['tarih', 'nobet_turu', 'vardiya', 'aciklama']
        widgets = {
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'nobet_turu': forms.Select(attrs={'class': 'form-select'}),
            'vardiya': forms.Select(attrs={'class': 'form-select'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('tarih'):
            self.initial['tarih'] = date.today()

class NobetOlayKaydiForm(forms.ModelForm):
    class Meta:
        model = NobetOlayKaydi
        fields = ['saat', 'konu', 'detay']
        widgets = {
            'saat': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            # Konu alanı için datalist ekleniyor
            'konu': forms.TextInput(attrs={
                'class': 'form-control',
                'list': 'konu_datalist',
                'autocomplete': 'off'
            }),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'id': 'id_detay'}),
        }
