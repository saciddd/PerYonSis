from django import forms
from .models.personel import Personel, Kurum, Unvan, Brans
from .models.GeciciGorev import GeciciGorev
from .models.ResmiYazi import ResmiYazi
from .models.DurumBelgesi import DurumBelgesi
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
            'aday_memur': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
        
        # Bazı alanları zorunlu yap
        self.fields['tc_kimlik_no'].required = True
        self.fields['ad'].required = True
        self.fields['soyad'].required = True
        self.fields['kurum'].required = True
        
        # Tarih alanları için özel validasyon
        self.fields['dogum_tarihi'].required = False
        self.fields['atama_karar_tarihi'].required = False
        self.fields['goreve_baslama_tarihi'].required = False
        self.fields['memuriyete_baslama_tarihi'].required = False
        self.fields['kamu_baslangic_tarihi'].required = False
        self.fields['mazeret_baslangic'].required = False
        self.fields['mazeret_bitis'].required = False
    
    def clean_tc_kimlik_no(self):
        tc_kimlik_no = self.cleaned_data.get('tc_kimlik_no')
        if tc_kimlik_no:
            # TC Kimlik No validasyonu
            if not tc_kimlik_no.isdigit() or len(tc_kimlik_no) != 11:
                raise forms.ValidationError("TC Kimlik No 11 haneli sayı olmalıdır.")
        return tc_kimlik_no
    
    def clean_eposta(self):
        eposta = self.cleaned_data.get('eposta')
        if eposta and '@' not in eposta:
            raise forms.ValidationError("Geçerli bir e-posta adresi giriniz.")
        return eposta
    
    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if telefon:
            # Telefon numarası temizleme
            telefon = telefon.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not telefon.isdigit():
                raise forms.ValidationError("Telefon numarası sadece rakam içermelidir.")
        return telefon

class KurumForm(forms.ModelForm):
    class Meta:
        model = Kurum
        fields = ['ad']

class UnvanForm(forms.ModelForm):
    class Meta:
        model = Unvan
        fields = ['ad', 'sinif']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'sinif': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ad'].required = True
        self.fields['sinif'].required = True
        self.fields['sinif'].choices = [
            ('', 'Sınıf seçiniz'),
            ('S.H.S.', 'S.H.S.'),
            ('G.İ.H.', 'G.İ.H.'),
            ('T.H.S.', 'T.H.S.'),
            ('BİLİNMİYOR', 'BİLİNMİYOR'),
        ]

class BransForm(forms.ModelForm):
    class Meta:
        model = Brans
        fields = ['ad', 'unvan']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'unvan': forms.Select(attrs={'class': 'form-select', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ad'].required = True
        self.fields['unvan'].required = True
        self.fields['unvan'].empty_label = "Unvan seçiniz"

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

class ResmiYaziForm(forms.ModelForm):
    class Meta:
        model = ResmiYazi
        fields = ['ad', 'metin']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Şablon Adı'}),
            'metin': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Resmi yazı metni'}),
        }


class DurumBelgesiForm(forms.ModelForm):
    class Meta:
        from .models import DurumBelgesi
        model = DurumBelgesi
        fields = ['ad', 'metin']
        widgets = {
            'ad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Belge Adı'}),
            'metin': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Durum belgesi metni'}),
        }