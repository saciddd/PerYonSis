# forms.py
from django import forms
from .models import Mesai_Tanimlari, ResmiTatil, YarimZamanliCalisma

class MesaiTanimForm(forms.ModelForm):
    class Meta:
        model = Mesai_Tanimlari
        fields = '__all__'
        widgets = {
            'Saat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08:00 16:00'}),
            'CKYS_BTF_Karsiligi': forms.TextInput(attrs={'class': 'form-control'}),
            'AraDinlenme': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25', 'min': '0', 'placeholder': 'Saat cinsinden(Örn: 1.5)'}),
            'Renk': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'GunduzMesaisi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'AksamMesaisi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'GeceMesaisi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'IseGeldi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'SonrakiGuneSarkiyor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'GecerliMesai': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ResmiTatilForm(forms.ModelForm):
    class Meta:
        model = ResmiTatil
        fields = ['TatilTarihi', 'Aciklama', 'TatilTipi', 'BayramMi', 'ArefeMi']
        widgets = {
            'TatilTarihi': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'Aciklama': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Tatil açıklaması'}
            ),
            'TatilTipi': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'BayramMi': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
            'ArefeMi': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }
        labels = {
            'TatilTarihi': 'Tatil Tarihi',
            'Aciklama': 'Açıklama',
            'TatilTipi': 'Tatil Tipi',
            'BayramMi': 'Bayram mı?',
            'ArefeMi': 'Arefe mi?',
        }

class YarimZamanliCalismaForm(forms.ModelForm):
    class Meta:
        model = YarimZamanliCalisma
        fields = ['baslangic_tarihi', 'bitis_tarihi', 'aciklama']
        widgets = {
            'baslangic_tarihi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bitis_tarihi': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'aciklama': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }