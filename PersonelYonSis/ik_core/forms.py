from django import forms
from .models.personel import Personel, Kurum, Unvan, Brans
from .models.GeciciGorev import GeciciGorev
from .models.valuelists import (
    TESKILAT_DEGERLERI, EGITIM_DEGERLERI, MAZERET_DEGERLERI,
    AYRILMA_NEDENI_DEGERLERI, ENGEL_DERECESI_DEGERLERI # Add necessary value lists
)

class PersonelForm(forms.ModelForm):
    class Meta:
        model = Personel
        fields = '__all__'
        widgets = {
            'tc_kimlik_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'T.C. Kimlik No'}),
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ad'}),
            'soyad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soyad'}),
            'dogum_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cinsiyet': forms.Select(attrs={'class': 'form-select'}),
            'sicil_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sicil No'}),
            'unvan': forms.Select(attrs={'class': 'form-select'}),
            'brans': forms.Select(attrs={'class': 'form-select', 'required': False}),
            'kurum': forms.Select(attrs={'class': 'form-select'}),
            'kadro_yeri': forms.Select(attrs={'class': 'form-select'}),
            'fiili_gorev_yeri': forms.Select(attrs={'class': 'form-select'}),
            'kadrolu_personel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'atama_karar_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'atama_karar_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Atama Karar No'}),
            'goreve_baslama_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'memuriyete_baslama_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'kamu_baslangic_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'teskilat': forms.Select(attrs={'class': 'form-select'}),
            'emekli_sicil_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emekli Sicil No'}),
            'tahsil_durumu': forms.Select(choices=EGITIM_DEGERLERI, attrs={'class': 'form-select'}),
            'aile_hek_sozlesmesi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mazeret_durumu': forms.Select(attrs={'class': 'form-select'}),
            'mazeret_baslangic': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'mazeret_bitis': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ozel_durumu': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'ozel_durumu_aciklama': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'engel_orani': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Engel Oranı'}),
            'vergi_indirimi': forms.Select(attrs={'class': 'form-select'}),
            'memur_devreden_izin': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Devreden İzin'}),
            'memur_hak_ettigi_izin': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Hak Ettiği İzin'}),
            'adres': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telefon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefon'}),
            'eposta': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta'}),
            'ayrilma_tarihi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ayrilma_nedeni': forms.Select(attrs={'class': 'form-select'}),
            'ayrilma_detay': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'dhy': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sgk': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dss': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shcek': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Branş alanına boş seçenek ekle
        if 'brans' in self.fields:
            self.fields['brans'].empty_label = "Branş seçiniz"
            self.fields['brans'].required = False

class KurumForm(forms.ModelForm):
    class Meta:
        model = Kurum
        fields = ['ad']

class UnvanForm(forms.ModelForm):
    class Meta:
        model = Unvan
        fields = ['ad', 'sinif']

class BransForm(forms.ModelForm):
    class Meta:
        model = Brans
        fields = ['ad', 'unvan']

class GeciciGorevForm(forms.ModelForm):
    class Meta:
        model = GeciciGorev
        fields = ['gecici_gorev_tipi', 'gecici_gorev_baslangic', 'gecici_gorev_bitis', 'asil_kurumu', 'gorevlendirildigi_birim']
        widgets = {
            'gecici_gorev_tipi': forms.Select(choices= (('Gidis', 'Gidiş'),('Gelis', 'Geliş'),), attrs={'class': 'form-select'}),
            'gecici_gorev_baslangic': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gecici_gorev_bitis': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'asil_kurumu': forms.TextInput(attrs={'class': 'form-control'}),
            'gorevlendirildigi_birim': forms.TextInput(attrs={'class': 'form-control'}),
        }
