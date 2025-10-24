from django import forms
from .models import NobetDefteri, NobetOlayKaydi, KontrolSoru, KontrolFormu, KontrolCevap, NobetciTekniker
from datetime import date

class NobetDefteriForm(forms.ModelForm):
    class Meta:
        model = NobetDefteri
        fields = ['tarih', 'nobet_turu', 'aciklama']
        widgets = {
            'tarih': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'nobet_turu': forms.Select(attrs={'class': 'form-select'}),
            'aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('tarih'):
            self.initial['tarih'] = date.today()

class NobetOlayKaydiForm(forms.ModelForm):
    class Meta:
        model = NobetOlayKaydi
        fields = ['saat', 'konu', 'detay', 'onemli']
        widgets = {
            'saat': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            # Konu alanı için datalist ekleniyor
            'konu': forms.TextInput(attrs={
                'class': 'form-control',
                'list': 'konu_datalist',
                'autocomplete': 'off'
            }),
            'detay': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'id': 'id_detay'}),
            'onemli': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class KontrolFormuForm(forms.ModelForm):
    class Meta:
        model = KontrolFormu
        # nobet_defteri alanına NobetDefteri otomatik atanacak
        fields = []


class KontrolCevapForm(forms.ModelForm):
    class Meta:
        model = KontrolCevap
        fields = ['cevap', 'aciklama']
        widgets = {
            'cevap': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'aciklama': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


# Dinamik form: soruları tek tek formset içine alacağız
KontrolCevapFormSet = forms.modelformset_factory(
    KontrolCevap,
    form=KontrolCevapForm,
    extra=0,
    can_delete=False
)


class DinamikKontrolForm(forms.Form):
    def __init__(self, *args, sorular=None, **kwargs):
        super().__init__(*args, **kwargs)
        if sorular:
            for soru in sorular:
                # Değerleri string olarak kullanıyoruz ('True' / 'False').
                # required=False olduğunda seçilmemiş (null) durumda hiçbir radio seçili olmaz.
                self.fields[f"soru_{soru.id}_cevap"] = forms.ChoiceField(
                    choices=[('True', "E"), ('False', "H")],
                    widget=forms.RadioSelect,
                    required=False,
                    label=soru.soru_metni
                )
                self.fields[f"soru_{soru.id}_aciklama"] = forms.CharField(
                    required=False,
                    widget=forms.Textarea(attrs={"rows": 1, "class": "form-control"})
                )

class KontrolSoruForm(forms.ModelForm):
    class Meta:
        model = KontrolSoru
        fields = ['soru_metni', 'aktif']
        widgets = {
            'soru_metni': forms.TextInput(attrs={'class': 'form-control'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class NobetciTeknikerForm(forms.ModelForm):
    class Meta:
        model = NobetciTekniker
        fields = ['tekniker_adi', 'gelis_saati', 'ayrilis_saati']
        labels = {
            'tekniker_adi': '',
        }
        widgets = {
            'tekniker_adi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'İcap Personeli Adı'}),
            'gelis_saati': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'placeholder': 'Geliş Saati'}),
            'ayrilis_saati': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'placeholder': 'Ayrılış Saati'}),
        }
