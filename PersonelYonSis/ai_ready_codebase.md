# PERSONELYÖNSİS - ÇİZELGE 657 MODÜLÜ KOD YAPISI VE İŞ AKIŞLARI
Bu döküman, yapay zeka modelinin mevzuat eşleştirmesi yapabilmesi için otomatik üretilmiştir.

## 1. DOSYA HİYERARŞİSİ
```text
mercis657/
    admin.py
    apps.py
    export_logic.py
    forms.py
    models.py
    sync_kayseri_api.py
    tests.py
    urls.py
    utils.py
    valuelists.py
    views.py
    __init__.py
    docs/
    management/
        __init__.py
        commands/
            sync_izinler.py
            __init__.py
    static/
        mercis657/
            js/
    templates/
        mercis657/
            partials/
            pdf/
        partials/
    templatetags/
        mercis_filters.py
        __init__.py
    views/
        bildirim_views.py
        birim_views.py
        cizelge_edit_views.py
        cizelge_kontrol_views.py
        ek_mesai_views.py
        fazla_mesai_views.py
        gunluk_izin_takibi_views.py
        ilk_liste_views.py
        imza_cizelgeleri_views.py
        izin_views.py
        liste_views.py
        main_views.py
        mazeret_views.py
        mesai_views.py
        personel_islem_views.py
        personel_views.py
        personel_yonetim_views.py
        raporlama_views.py
        riskli_calisma_views.py
        stop_views.py
        tanimlamalar_views.py
        vardiya_dagilim_views.py
        yonetici_views.py
        __init__.py
```

---

## 2. DOSYA İÇERİKLERİ VE KODLAR

### Dosya: admin.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\admin.py`

```python
from django.contrib import admin

# Register your models here.

```

---

### Dosya: apps.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\apps.py`

```python
from django.apps import AppConfig


class Mercis657Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mercis657'

```

---

### Dosya: export_logic.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\export_logic.py`

```python
import os

# Taranmasını istediğin klasör ve dosyalar (Burayı kendi yapına göre güncelle)
# Sadece iş kurallarının (657 modülünün) olduğu klasörü hedef göstermen yeterli.
TARGET_DIR = "d:/Github/PerYonSis/PersonelYonSis/mercis657" 
OUTPUT_FILE = "ai_ready_codebase.md"
ALLOWED_EXTENSIONS = ['.py'] # İhtiyaca göre .js, .html eklenebilir

def generate_ai_ready_file():
    print("🚀 Kod analiz scripti başlatıldı...")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        outfile.write("# PERSONELYÖNSİS - ÇİZELGE 657 MODÜLÜ KOD YAPISI VE İŞ AKIŞLARI\n")
        outfile.write("Bu döküman, yapay zeka modelinin mevzuat eşleştirmesi yapabilmesi için otomatik üretilmiştir.\n\n")
        
        # 1. Klasör Ağacını Çıkaralım (AI'ın sistemi anlaması için)
        outfile.write("## 1. DOSYA HİYERARŞİSİ\n```text\n")
        for root, dirs, files in os.walk(TARGET_DIR):
            # Git ve cache klasörlerini pas geç
            if any(p in root for p in ['__pycache__', '.git', 'migrations']):
                continue
            level = root.replace(TARGET_DIR, '').count(os.sep)
            indent = ' ' * 4 * (level)
            outfile.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if any(f.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    outfile.write(f'{subindent}{f}\n')
        outfile.write("```\n\n---\n\n")
        
        # 2. Dosya İçeriklerini Ekleyelim
        outfile.write("## 2. DOSYA İÇERİKLERİ VE KODLAR\n\n")
        for root, dirs, files in os.walk(TARGET_DIR):
            if any(p in root for p in ['__pycache__', '.git', 'migrations']):
                continue
            for file in files:
                if any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, TARGET_DIR)
                    
                    print(f"Okunuyor: {relative_path}")
                    outfile.write(f"### Dosya: {relative_path}\n")
                    outfile.write(f"Path: `{full_path}`\n\n")
                    outfile.write("```python\n")
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"# Dosya okunurken hata oluştu: {str(e)}")
                        
                    outfile.write("\n```\n\n---\n\n")
                    
    print(f"✅ İşlem tamamlandı! '{OUTPUT_FILE}' dosyası oluşturuldu. Bu dosyayı AI modeline yükleyebilirsin.")

if __name__ == "__main__":
    generate_ai_ready_file()
```

---

### Dosya: forms.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\forms.py`

```python
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
```

---

### Dosya: models.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\models.py`

```python
from decimal import Decimal
from django.db import models
import datetime
from datetime import date, timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()

class Kurum(models.Model):
    ad = models.CharField(max_length=100, unique=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

class UstBirim(models.Model):
    ad = models.CharField(max_length=100, unique=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

class Idareci(models.Model):
    ad = models.CharField(max_length=100, unique=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

class Bina(models.Model):
    ad = models.CharField(max_length=100)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

class Birim(models.Model):
    BirimID = models.AutoField(primary_key=True)
    BirimAdi = models.CharField(max_length=100)
    NormalNobetKodu = models.PositiveIntegerField(null=True, blank=True, default=1)
    BayramNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    RiskliNormalNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    RiskliBayramNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    NormalGeceNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    BayramGeceNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    RiskliNormalGeceNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    RiskliBayramGeceNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    Pasif = models.BooleanField(default=False)

    Kurum = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, blank=True)
    UstBirim = models.ForeignKey(UstBirim, on_delete=models.SET_NULL, null=True, blank=True)
    Idareci = models.ForeignKey(Idareci, on_delete=models.SET_NULL, null=True, blank=True)
    Bina = models.ForeignKey(Bina, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.BirimAdi


class UserBirim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mercis657_birimleri')
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE, related_name='mercis657_kullanicilari')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'birim')
        verbose_name = "Kullanıcı Birim Yetkisi"
        verbose_name_plural = "Kullanıcı Birim Yetkileri"

    def __str__(self):
        return f"{self.user.username} - {self.birim.BirimAdi}"

class PersonelListesi(models.Model):
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE, related_name='personel_listeleri')
    yil = models.PositiveIntegerField()
    ay = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    aciklama = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('birim', 'yil', 'ay')
        verbose_name = 'Personel Listesi'
        verbose_name_plural = 'Personel Listeleri'

    def __str__(self):
        return f"{self.birim.BirimAdi} - {self.ay}/{self.yil}"

class SabitMesai(models.Model):
    aralik = models.CharField(max_length=20)
    ara_dinlenme = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
class PersonelListesiKayit(models.Model):
    liste = models.ForeignKey(PersonelListesi, on_delete=models.CASCADE, related_name='kayitlar')
    personel = models.ForeignKey('Personel', on_delete=models.CASCADE)
    radyasyon_calisani = models.BooleanField(default=False)
    sabit_mesai = models.ForeignKey(SabitMesai, null=True, blank=True, on_delete=models.SET_NULL)
    sira_no = models.PositiveIntegerField(null=True, blank=True)
    is_gunduz_personeli = models.BooleanField(
        default=True,
        help_text="True: Gündüz Personeli, False: Nöbetli Çalışan"
    )

    class Meta:
        unique_together = ('liste', 'personel')
        verbose_name = 'Personel Listesi Kayıt'
        verbose_name_plural = 'Personel Listesi Kayıtları'

    def __str__(self):
        return f"{self.liste} - {self.personel}"

class Personel(models.Model):
    PersonelID = models.AutoField(primary_key=True)
    PersonelTCKN = models.BigIntegerField(unique=True)
    PersonelName = models.CharField(max_length=100, null=False)
    PersonelSurname = models.CharField(max_length=100, null=False)
    PersonelTitle = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.PersonelName} ({self.PersonelTCKN})"

class Mesai(models.Model):
    MesaiID = models.AutoField(primary_key=True)
    Personel = models.ForeignKey('Personel', on_delete=models.CASCADE, related_name='mercis657_mesai_personel')
    MesaiDate = models.DateField(null=False)
    MesaiTanim = models.ForeignKey('Mesai_Tanimlari', on_delete=models.CASCADE, null=True, related_name='mercis657_mesai_tanimlari')
    Izin = models.ForeignKey('Izin', on_delete=models.SET_NULL, null=True, blank=True, related_name='mercis657_mesai_izin')
    Icap = models.BooleanField(default=False)
    OnayDurumu = models.BooleanField(default=True)
    OnayTarihi = models.DateTimeField(null=True, blank=True)
    Onaylayan = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='mercis657_mesai_onaylayan')
    Degisiklik = models.BooleanField(default=False)  # True: Değişiklik var, False: Değişiklik yok
    SistemdekiIzin = models.BooleanField(default=False)  # True: İzin var, False: İzin yok
    MesaiNotu = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='mercis657_mesai_ekleyen')
    
    RISKLI_TAM = 'full'
    RISKLI_NOBET = 'nobet'

    RISKLI_CHOICES = [
        (RISKLI_TAM, 'Tam Riskli'),
        (RISKLI_NOBET, 'Nöbet Riskli'),
    ]

    riskli_calisma = models.CharField(
        max_length=10,
        choices=RISKLI_CHOICES,
        default=None,
        null=True,
        blank=True
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Personel', 'MesaiDate'], name='unique_personel_mesaidate')
        ]
    
    def __str__(self):
        return f"{self.Personel.PersonelName} - {self.MesaiDate}"

class MesaiYedek(models.Model):
    mesai = models.ForeignKey('Mesai', on_delete=models.CASCADE, related_name='yedekler')
    MesaiTanim = models.ForeignKey('Mesai_Tanimlari', on_delete=models.SET_NULL, null=True, blank=True, related_name='mercis657_mesaiyedek_tanim')
    Izin = models.ForeignKey('Izin', on_delete=models.SET_NULL, null=True, blank=True, related_name='mercis657_mesaiyedek_izin')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='mercis657_mesaiyedek_ekleyen')

    class Meta:
        verbose_name = "Mesai Yedeği"
        verbose_name_plural = "Mesai Yedekleri"

    def __str__(self):
        return f"Yedek: {self.mesai.Personel.PersonelName} - {self.mesai.MesaiDate}"


class Mesai_Tanimlari(models.Model):
    Saat = models.CharField(max_length=11)
    GunduzMesaisi = models.BooleanField(default=False)
    AksamMesaisi = models.BooleanField(default=False)
    GeceMesaisi = models.BooleanField(default=False)
    IseGeldi = models.BooleanField(default=False)
    SonrakiGuneSarkiyor = models.BooleanField(default=False)
    AraDinlenme = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text="Mesai ara dinlenmesi saat cinsinden (örn: 1.5)"
    )
    GecerliMesai = models.BooleanField(default=True)
    CKYS_BTF_Karsiligi = models.CharField(max_length=100, null=True, blank=True)
    Sure = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text="Mesai süresi saat cinsinden (örn: 9.5)"
    )
    GeceCalismaSure = models.DecimalField(
        max_digits=4, decimal_places=2,
        null=True, blank=True,
        help_text="20:00–08:00 arası gece çalışma süresi saat cinsinden (örn: 9.5)"
    )
    Renk = models.CharField(max_length=7, null=True)

    def calculate_sure(self):
        """Mesai süresini saat cinsinden (ondalıklı) hesapla."""
        start, end = self.Saat.split(' ')
        start_time = self._parse_time(start)
        end_time = self._parse_time(end)

        if self.SonrakiGuneSarkiyor:
            end_time += timedelta(hours=24)

        total_seconds = (end_time - start_time).total_seconds()
        hours = Decimal(total_seconds / 3600).quantize(Decimal("0.01"))

        # Ara dinlenme çıkar
        if self.AraDinlenme:
            hours -= self.AraDinlenme

        if hours < 0:
            hours = Decimal("0.00")

        self.Sure = hours
        return hours

    def _parse_time(self, time_str):
        """'HH:MM' formatında bir saat dilimini timedelta olarak döndürür."""
        hours, minutes = map(int, time_str.split(':'))
        return timedelta(hours=hours, minutes=minutes)
    
    def save(self, *args, **kwargs):
        self.Sure = self.calculate_sure()
        self.GeceCalismaSure = self.calculate_gece_suresi()
        super().save(*args, **kwargs)

    def calculate_gece_suresi(self):
        """
        20:00–08:00 arası gece çalışma süresini saat cinsinden hesaplar.
        Ara dinlenme hesaba katılmaz.
        """
        if not self.Saat:
            return Decimal("0.00")
            
        start_str, end_str = self.Saat.split(' ')
        start = self._parse_time(start_str)
        end = self._parse_time(end_str)

        # Mesai ertesi güne sarkıyorsa
        if self.SonrakiGuneSarkiyor or end <= start:
            end += timedelta(hours=24)

        # Gece aralıkları
        # 1. Günün başındaki gece (00:00 - 08:00)
        win1_start = timedelta(hours=0)
        win1_end = timedelta(hours=8)

        # 2. Akşam başlayan gece (20:00 - 08:00 ertesi gün => 20 - 32)
        win2_start = timedelta(hours=20)
        win2_end = timedelta(hours=32)

        def overlap(a_start, a_end, b_start, b_end):
            """İki zaman aralığının kesişim süresi (timedelta)"""
            latest_start = max(a_start, b_start)
            earliest_end = min(a_end, b_end)
            return max(timedelta(0), earliest_end - latest_start)

        gece_sure = timedelta(0)

        gece_sure += overlap(start, end, win1_start, win1_end)
        gece_sure += overlap(start, end, win2_start, win2_end)

        hours = Decimal(gece_sure.total_seconds() / 3600).quantize(Decimal("0.01"))

        if hours < 0:
            hours = Decimal("0.00")

        return hours

    def __str__(self):
        return f"{self.Saat} ({self.Sure} saat)"

class Izin(models.Model):
    ad = models.CharField(max_length=100, unique=False)
    kod = models.CharField(max_length=20, unique=False)
    fm_karsiligi = models.CharField(max_length=100)

    def __str__(self):
        return self.ad

class MazeretKaydi(models.Model):
    personel = models.ForeignKey('Personel', on_delete=models.CASCADE, related_name='mazeret_kayitlari')
    baslangic_tarihi = models.DateField()
    bitis_tarihi = models.DateField()
    gunluk_azaltim_saat = models.DecimalField(max_digits=4, decimal_places=2, help_text="Günlük azaltım saati (örn: 3.00, 1.50)")
    aciklama = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Mazeret Kaydı"
        verbose_name_plural = "Mazeret Kayıtları"

    def __str__(self):
        return f"{self.personel.PersonelName} - {self.baslangic_tarihi} / {self.bitis_tarihi}"

class ResmiTatil(models.Model):
    TatilID = models.AutoField(primary_key=True)
    TatilTarihi = models.DateField()
    Aciklama = models.CharField(max_length=200)
    TatilTipi = models.CharField(
        max_length=10,
        choices=[('TAM', 'Tam Gün'), ('YARIM', 'Yarım Gün')],
        default='TAM'
    )
    BayramMi = models.BooleanField(default=False)
    ArefeMi = models.BooleanField(default=False)

    class Meta:
        ordering = ['TatilTarihi']

    def __str__(self):
        return f"{self.TatilTarihi.strftime('%d.%m.%Y')} - {self.Aciklama}"
    
class Bildirim(models.Model):
    BildirimID = models.AutoField(primary_key=True)
    PersonelListesi = models.ForeignKey(PersonelListesi, on_delete=models.CASCADE, related_name='mercis657_bildirimler')
    Personel = models.ForeignKey('Personel', on_delete=models.CASCADE, related_name='mercis657_bildirimler')
    DonemBaslangic = models.DateField()
    
    # Mesai süreleri (saat cinsinden)
    NormalFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    BayramFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    RiskliNormalFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    RiskliBayramFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Gece çalışma süreleri (saat cinsinden)
    GeceNormalFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    GeceBayramFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    GeceRiskliNormalFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    GeceRiskliBayramFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # İcap süreleri (saat cinsinden)
    NormalIcap = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    BayramIcap = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Günlük detaylar
    MesaiDetay = models.JSONField(null=True, blank=True)  # {date: MesaiTanim.Saat}
    IcapDetay = models.JSONField(null=True, blank=True)   # {date: MesaiTanim.Saat}
    
    # İşlem bilgileri
    OlusturanKullanici = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mercis657_olusturan_bildirimler')
    OlusturmaTarihi = models.DateTimeField(auto_now_add=True)
    OnaylayanKullanici = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mercis657_onaylayan_bildirimler')
    OnayTarihi = models.DateTimeField(null=True)
    OnayDurumu = models.IntegerField(default=0)  # 0: Bekliyor, 1: Onaylandı
    SilindiMi = models.BooleanField(default=False)
    MutemetKilit = models.BooleanField(default=False)  # Kilit durumu
    MutemetKilitUser = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mercis657_mutemet_kilit_kullanicilar'
    )  # Kilitleyen kullanıcı
    MutemetKilitTime = models.DateTimeField(null=True, blank=True)  # Kilitleme zamanı

    class Meta:
        # Unique per person and period
        unique_together = [['Personel', 'DonemBaslangic']]

    @property
    def ToplamFazlaMesai(self):
        """Toplam fazla mesai saati"""
        return (self.NormalFazlaMesai + self.BayramFazlaMesai + 
                self.RiskliNormalFazlaMesai + self.RiskliBayramFazlaMesai +
                self.GeceNormalFazlaMesai + self.GeceBayramFazlaMesai +
                self.GeceRiskliNormalFazlaMesai + self.GeceRiskliBayramFazlaMesai)

    @property
    def ToplamIcap(self):
        """Toplam icap saati"""
        return self.NormalIcap + self.BayramIcap

class YarimZamanliCalisma(models.Model):
    personel = models.ForeignKey('Personel', on_delete=models.CASCADE, related_name="yarim_zamanli_donemler")
    baslangic_tarihi = models.DateField()
    bitis_tarihi = models.DateField(null=True, blank=True)
    aciklama = models.TextField(blank=True, null=True)

    # Günlere göre mesai planı
    # {"Pazartesi": [1, 2], "Çarşamba": [5]}  -> Mesai_Tanimlari id listesi
    haftalik_plan = models.JSONField()

    def __str__(self):
        return f"{self.personel} ({self.baslangic_tarihi} - {self.bitis_tarihi or 'devam'})"

class StopKaydi(models.Model):
    mesai = models.ForeignKey('Mesai', on_delete=models.CASCADE, related_name="mercis657_stoplar")
    StopBaslangic = models.TimeField()
    StopBitis = models.TimeField()
    Sure = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # saat cinsinden (örn: 1.5)
    Aciklama = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def hesapla_sure(self):
        """Stop süresini saat cinsinden hesaplar."""
        if self.StopBaslangic and self.StopBitis:
            # datetime.time objelerini datetime.datetime objelerine çevirerek fark alalım
            # Eşitlik durumunda (örn: create sırasında) zaten datetime olabilirler, 
            # ancak TimeField'dan çekildiklerinde time objesi olurlar.
            
            if isinstance(self.StopBaslangic, datetime.datetime):
                bas_dt = self.StopBaslangic
            else:
                bas_dt = datetime.datetime.combine(date.today(), self.StopBaslangic)
                
            if isinstance(self.StopBitis, datetime.datetime):
                bit_dt = self.StopBitis
            else:
                bit_dt = datetime.datetime.combine(date.today(), self.StopBitis)

            if bit_dt <= bas_dt:
                bit_dt += timedelta(days=1)
                
            delta = bit_dt - bas_dt
            self.Sure = Decimal(delta.total_seconds() / 3600).quantize(Decimal("0.01"))
        else:
            self.Sure = Decimal('0.00')
        return self.Sure

    def save(self, *args, **kwargs):
        self.hesapla_sure()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mesai} stop: {self.Sure} saat"

class EkMesai(models.Model):
    mesai = models.ForeignKey('Mesai', on_delete=models.CASCADE, related_name="mercis657_ek_mesailer")
    Baslangic = models.TimeField()
    Bitis = models.TimeField()
    Sure = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    Aciklama = models.TextField(blank=True)
    Riskli = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def hesapla_sure(self):
        """Ek mesai süresini saat cinsinden hesaplar."""
        if self.Baslangic and self.Bitis:
            if isinstance(self.Baslangic, datetime.datetime):
                bas_dt = self.Baslangic
            else:
                bas_dt = datetime.datetime.combine(date.today(), self.Baslangic)
                
            if isinstance(self.Bitis, datetime.datetime):
                bit_dt = self.Bitis
            else:
                bit_dt = datetime.datetime.combine(date.today(), self.Bitis)

            if bit_dt <= bas_dt:
                bit_dt += timedelta(days=1)
                
            delta = bit_dt - bas_dt
            self.Sure = Decimal(delta.total_seconds() / 3600).quantize(Decimal("0.01"))
        else:
            self.Sure = Decimal('0.00')
        return self.Sure

    def save(self, *args, **kwargs):
        self.hesapla_sure()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mesai} ek mesai: {self.Sure} saat"

class IlkListe(models.Model):
    PersonelListesi = models.ForeignKey(
        'PersonelListesi',
        on_delete=models.CASCADE,
        related_name='mercis657_ilk_liste'
    )

    # JSON snapshot
    Veriler = models.JSONField(null=True, blank=True)

    # İşlem bilgileri
    OlusturanKullanici = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='mercis657_olusturan_ilk_liste'
    )
    OlusturmaTarihi = models.DateTimeField(auto_now_add=True)

    OnaylayanKullanici = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='mercis657_onaylayan_ilk_liste'
    )
    OnayTarihi = models.DateTimeField(null=True, blank=True)
    OnayDurumu = models.BooleanField(default=False)

    class Meta:
        verbose_name = "İlk Liste Bildirimi"
        verbose_name_plural = "İlk Liste Bildirimleri"
        ordering = ['-OlusturmaTarihi']

    def __str__(self):
        return f"{self.PersonelListesi.birim} - {self.PersonelListesi.yil}/{self.PersonelListesi.ay} İlk Liste"

    def onayla(self, kullanici):
        """İlk listeyi onaylar ve bilgileri kaydeder."""
        self.OnayDurumu = True
        self.OnaylayanKullanici = kullanici
        self.OnayTarihi = timezone.now()
        self.save()

    def onay_kaldir(self, kullanici):
        """İlk listeyi onayını kaldırır ve bilgileri kaydeder."""
        self.OnayDurumu = False
        self.OnaylayanKullanici = kullanici
        self.OnayTarihi = timezone.now()
        self.save()

class UserMesaiFavori(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favori_mesaileri")
    mesai = models.ForeignKey(Mesai_Tanimlari, on_delete=models.CASCADE, related_name="favori_kullanicilar")

    class Meta:
        unique_together = ('user', 'mesai')
        verbose_name = "Favori Mesai"
        verbose_name_plural = "Favori Mesailer"

    def __str__(self):
        return f"{self.user} → {self.mesai.Saat}"

class MesaiKontrol(models.Model):
    mesai = models.ForeignKey('Mesai', on_delete=models.CASCADE, related_name='mesai_kontrolleri')
    kontrol = models.BooleanField(default=False)
    kontrol_tarihi = models.DateTimeField(auto_now_add=True)
    kontrol_yapan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Mesai Kontrol'
        verbose_name_plural = 'Mesai Kontrolleri'
        unique_together = ('mesai',)
```

---

### Dosya: sync_kayseri_api.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\sync_kayseri_api.py`

```python
import json
import requests

API_URL = "http://10.38.8.115:5000/api/v1/kayseri/mesai/sync"
API_KEY = "dkod_kayseri_7b3f9a2e1d5c8f4061e2b7a9d3c5f812"

def sync_kayseri_mesai(liste_id: int):
    """
    Kayseri entegrasyonu için senkron mesai gönderimi yapar ve API sonucunu döner.
    """
    try:
        from .models import PersonelListesi, Mesai
        
        try:
            liste = PersonelListesi.objects.select_related('birim').get(id=liste_id)
        except PersonelListesi.DoesNotExist:
            return {"durum": "HATA", "mesaj": "Personel listesi bulunamadı."}
            
        birim_id = liste.birim.BirimID
        birim_adi = liste.birim.BirimAdi
        donem = f"{liste.yil}-{liste.ay:02d}"
        
        # Listedeki personeller
        personel_ids = liste.kayitlar.values_list('personel_id', flat=True)
        
        # Sadece M1 ve M2 notuna sahip olan mesaileri çekeceğiz
        mesailer = Mesai.objects.filter(
            Personel_id__in=personel_ids,
            MesaiDate__year=liste.yil,
            MesaiDate__month=liste.ay,
            MesaiNotu__in=["M1", "M2"]
        ).select_related('Personel', 'MesaiTanim')
        
        mesailar_payload = []
        
        for m in mesailer:
            baslangic = ""
            bitis = ""
            if m.MesaiTanim and m.MesaiTanim.Saat:
                try:
                    parts = m.MesaiTanim.Saat.split(' ')
                    if len(parts) >= 2:
                        baslangic = parts[0]
                        bitis = parts[1]
                    else:
                        baslangic = parts[0]
                        bitis = parts[0]
                except Exception:
                    pass
            
            if not baslangic or not bitis:
                continue
                
            mesailar_payload.append({
                "tckn": str(m.Personel.PersonelTCKN),
                "tarih": m.MesaiDate.strftime("%Y-%m-%d"),
                "baslangic": baslangic,
                "bitis": bitis,
                "mesaiNotu": m.MesaiNotu,
                "onayDurumu": m.OnayDurumu,
                "izinli": bool(m.SistemdekiIzin or getattr(m, 'Izin_id', None))
            })
            
        # Eğer gönderilecek hiç M1 veya M2 notlu kayıt yoksa işlemi atla
        if not mesailar_payload:
            return {"durum": "BOS", "mesaj": "Gönderilecek M1/M2 notu olan kayıt bulunamadı."}
            
        payload = {
            "birimId": birim_id,
            "birimAdi": birim_adi,
            "donem": donem,
            "mesailar": mesailar_payload
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }
        
        response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"durum": "HATA", "mesaj": f"API Bağlantı Hatası: HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
         return {"durum": "HATA", "mesaj": "Sunucuya bağlanırken zaman aşımı meydana geldi."}
    except requests.exceptions.RequestException as e:
         return {"durum": "HATA", "mesaj": f"Sunucuya bağlanırken ağ hatası oluştu: {str(e)}"}
    except Exception as e:
         return {"durum": "HATA", "mesaj": f"Beklenmeyen bir hata oluştu: {str(e)}"}

```

---

### Dosya: tests.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\tests.py`

```python
import os
import sys
import django

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PersonelYonSis.settings')
django.setup()

from mercis657.models import SabitMesai

def test_sabit_mesailer():
    print("=== SabitMesai Verilerini Test Etme ===")
    print()
    
    try:
        # Raw SQL ile verileri çek
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, aralik, ara_dinlenme FROM mercis657_sabitmesai")
            rows = cursor.fetchall()
        
        print(f"Toplam {len(rows)} adet SabitMesai kaydi bulundu.")
        print()
        
        for i, (id, aralik, ara_dinlenme) in enumerate(rows, 1):
            print(f"{i}. Kayit:")
            print(f"   ID: {id}")
            print(f"   Aralik: {aralik}")
            print(f"   Ara Dinlenme (Raw): {ara_dinlenme}")
            
            # ara_dinlenme değerini test et
            try:
                if ara_dinlenme is not None:
                    float(ara_dinlenme)
                    print(f"   OK - ara_dinlenme gecerli: {ara_dinlenme}")
                else:
                    print(f"   INFO - ara_dinlenme null")
            except (ValueError, TypeError) as e:
                print(f"   HATA - ara_dinlenme HATALI: {ara_dinlenme} - Hata: {e}")
            
            print()
            
    except Exception as e:
        print(f"HATA olustu: {e}")

def test_problemli_kayitlar():
    print("=== Problemli Kayitlari Bulma ===")
    print()
    
    problemli_kayitlar = []
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, aralik, ara_dinlenme FROM mercis657_sabitmesai")
            rows = cursor.fetchall()
        
        for id, aralik, ara_dinlenme in rows:
            try:
                if ara_dinlenme is not None:
                    float(ara_dinlenme)
            except (ValueError, TypeError):
                problemli_kayitlar.append((id, aralik, ara_dinlenme))
    except Exception as e:
        print(f"HATA olustu: {e}")
        return
    
    if problemli_kayitlar:
        print(f"HATA - {len(problemli_kayitlar)} adet problemli kayit bulundu:")
        for id, aralik, ara_dinlenme in problemli_kayitlar:
            print(f"   ID: {id}, Aralik: {aralik}, Ara Dinlenme: {ara_dinlenme}")
    else:
        print("OK - Tum kayitlar gecerli!")

def duzelt_problemli_kayitlar():
    print("=== Problemli Kayitlari Duzeltme ===")
    print()
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Problemli kayıtları bul
            cursor.execute("SELECT id, aralik, ara_dinlenme FROM mercis657_sabitmesai WHERE ara_dinlenme LIKE '%,%'")
            rows = cursor.fetchall()
        
        if rows:
            print(f"{len(rows)} adet problemli kayit bulundu, duzeltiliyor...")
            
            for id, aralik, ara_dinlenme in rows:
                # Virgülü nokta ile değiştir
                duzeltilmis = ara_dinlenme.replace(',', '.')
                print(f"   ID {id}: '{ara_dinlenme}' -> '{duzeltilmis}'")
                
                # Güncelle
                cursor.execute(
                    "UPDATE mercis657_sabitmesai SET ara_dinlenme = ? WHERE id = ?",
                    (duzeltilmis, str(id))
                )
            
            print("Duzeltme tamamlandi!")
        else:
            print("Problemli kayit bulunamadi.")
            
    except Exception as e:
        print(f"HATA olustu: {e}")

if __name__ == "__main__":
    test_sabit_mesailer()
    print("=" * 50)
    test_problemli_kayitlar()
    print("=" * 50)
    duzelt_problemli_kayitlar()
    print("=" * 50)
    print("Duzeltme sonrasi test:")
    test_sabit_mesailer()
```

---

### Dosya: urls.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\urls.py`

```python
from django.urls import path
from . import views
from .views import fazla_mesai_views, liste_views
from .views import personel_yonetim_views, cizelge_kontrol_views, riskli_calisma_views, ek_mesai_views
# from .views import main_views

app_name = 'mercis657'  # Namespace tanımlaması

urlpatterns = [
    # Personel Yönetimi
    path('personel-yonetim/', personel_yonetim_views.personel_yonetim, name='personel_yonetim'),
    path('personel-sorgula/', personel_yonetim_views.personel_sorgula, name='personel_sorgula'),
    path('personel/<int:personel_id>/listeler/', personel_yonetim_views.personel_listeleri, name='personel_listeleri_kisi'),
    # Yeni eklenen URL pattern'leri
    path('birim/<int:birim_id>/listeler/', liste_views.birim_listeleri, name='birim_listeleri'),
    path('liste/<int:liste_id>/personeller/', liste_views.liste_personeller, name='liste_personeller'),
    path('liste/<int:liste_id>/personel/<int:personel_id>/sil/', liste_views.personel_cikar, name='personel_cikar'),
    path('liste/<int:liste_id>/sil/', liste_views.liste_sil, name='liste_sil'),
    
    # Mevcut URL pattern'leri
    path('cizelge', views.cizelge, name='cizelge'),
    path('cizelge_kaydet', views.cizelge_kaydet, name='cizelge_kaydet'),
    path('favori-mesai-kaydet/', views.favori_mesai_kaydet, name='favori_mesai_kaydet'),
    path('fazla-mesai-hesapla', fazla_mesai_views.fazla_mesai_hesapla, name='fazla_mesai_hesapla'),
    path('fazla-mesai-hesapla-toplu/', fazla_mesai_views.fazla_mesai_hesapla_toplu, name='fazla_mesai_hesapla_toplu'),
    path('vardiya-tanimlari/', fazla_mesai_views.vardiya_tanimlari, name='vardiya_tanimlari'),
    path('cizelge-kontrol/', cizelge_kontrol_views.cizelge_kontrol, name='cizelge_kontrol'),
    path('export_excel/', views.excel_export, name='export_excel'),
    path('add_mesai_tanim/', views.add_mesai_tanim, name='add_mesai_tanim'),
    path('mesai_tanim_update/', views.mesai_tanim_update, name='mesai_tanim_update'),
    path('mesai-tanim-form/<int:pk>/', views.mesai_tanim_form, name='mesai_tanim_form'),
    path('delete-mesai-tanim/', views.delete_mesai_tanim, name='delete_mesai_tanim'),
    path('personel-listeleri/', views.personel_listeleri, name='personel_listeleri'),
    path('personel-listesi/olustur/', views.personel_listesi_olustur, name='personel_listesi_olustur'),
    path('personel-listesi/<int:liste_id>/', views.personel_listesi_detay, name='personel_listesi_detay'),
    path('personel-listesi/<int:liste_id>/ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel-listesi/<int:liste_id>/cikar/<int:personel_id>/', views.personel_cikar, name='personel_cikar'),
    path('birim-yonetim/', views.birim_yonetim, name='birim_yonetim'),
    path('birim-ekle/', views.birim_ekle, name='birim_ekle'),
    path('birim/<int:birim_id>/sil/', views.birim_sil, name='birim_sil'),
    path('birim/<int:birim_id>/yetki-ekle/', views.birim_yetki_ekle, name='birim_yetki_ekle'),
    path('birim/<int:birim_id>/yetki-sil/', views.birim_yetki_sil, name='birim_yetki_sil'),
    path('birim/<int:birim_id>/yetkililer/', views.birim_yetkililer, name='birim_yetkililer'),

    # Kullanıcı işlemleri
    path('kullanici/ara/', views.kullanici_ara, name='kullanici_ara'),

    # Birim Yönetimi API Endpoints
    path('birim/<int:birim_id>/detay/', views.birim_detay, name='birim_detay'),
    path('birim/<int:birim_id>/guncelle/', views.birim_guncelle, name='birim_guncelle'),

    path('kurum-ekle/', views.kurum_ekle, name='kurum_ekle'),
    path('kurum-guncelle/<int:pk>/', views.kurum_guncelle, name='kurum_guncelle'),
    path('kurum-toggle-aktif/<int:pk>/', views.kurum_toggle_aktif, name='kurum_toggle_aktif'),
    path('kurum-sil/<int:pk>/', views.kurum_sil, name='kurum_sil'),

    path('ust-birim-ekle/', views.ust_birim_ekle, name='ust_birim_ekle'),
    path('ust-birim-guncelle/<int:pk>/', views.ust_birim_guncelle, name='ust_birim_guncelle'),
    path('ust-birim-toggle-aktif/<int:pk>/', views.ust_birim_toggle_aktif, name='ust_birim_toggle_aktif'),
    path('ust-birim-sil/<int:pk>/', views.ust_birim_sil, name='ust_birim_sil'),

    path('onceki-donem-personel/<str:donem>/<int:birim_id>/', views.onceki_donem_personel, name='onceki_donem_personel'),
    path('personel/kaydet/', views.personel_kaydet, name='personel_kaydet'),
    path("yarim-zamanli-kaydet/<int:personel_id>/", views.yarim_zamanli_calisma_kaydet, name="yarim_zamanli_calisma_kaydet"),
    path("yarim-zamanli-sil/<int:pk>/", views.yarim_zamanli_calisma_sil, name="yarim_zamanli_calisma_sil"),
    path('cizelge/yazdir/', views.cizelge_yazdir, name='cizelge_yazdir'),
    path('cizelge-onay/', views.cizelge_onay, name='cizelge_onay'),
    path('imza_cizelgeleri_yazdir/', views.imza_cizelgeleri_yazdir, name='imza_cizelgeleri_yazdir'),
    path('mesai-onayla/<int:mesai_id>/', views.mesai_onayla, name='mesai_onayla'),
    path('mesai-reddet/<int:mesai_id>/', views.mesai_reddet, name='mesai_reddet'),
    path('toplu-onay/<int:birim_id>/<int:year>/<int:month>/', views.toplu_onay, name='toplu_onay'),
    path('tanimlamalar/', views.tanimlamalar, name='tanimlamalar'),

    path('idareci-toggle-aktif/<int:pk>/', views.idareci_toggle_aktif, name='idareci_toggle_aktif'),
    path('idareci-ekle/', views.idareci_ekle, name='idareci_ekle'),
    path('idareci-guncelle/<int:pk>/', views.idareci_guncelle, name='idareci_guncelle'),

    # İzin işlemleri
    path('izin-ekle/', views.izin_ekle, name='izin_ekle'),
    path('izin-guncelle/<int:pk>/', views.izin_guncelle, name='izin_guncelle'),
    
    # Personel profil ve mazeret işlemleri
    path('personel-profil/<int:personel_id>/<int:liste_id>/<int:year>/<int:month>/', views.personel_profil, name='personel_profil'),
    path('mazeret-ekle/', views.mazeret_ekle, name='mazeret_ekle'),
    path('mazeret-guncelle/<int:mazeret_id>/', views.mazeret_guncelle, name='mazeret_guncelle'),
    path('mazeret-sil/<int:mazeret_id>/', views.mazeret_sil, name='mazeret_sil'),
    path('radyasyon-toggle/<int:personel_id>/<int:liste_id>/', views.radyasyon_toggle, name='radyasyon_toggle'),
    path('hazir-mesai-ata/<int:personel_id>/<int:liste_id>/<int:year>/<int:month>/', views.hazir_mesai_ata, name='hazir_mesai_ata'),
    path('sabit-mesai-guncelle/', views.sabit_mesai_guncelle, name='sabit_mesai_guncelle'),
    
    # Stop işlemleri
    path('stop-ekle/<int:mesai_id>/', views.stop_ekle, name='stop_ekle'),
    path('stop-sil/<int:stop_id>/', views.stop_sil, name='stop_sil'),

    # Ek Mesai işlemleri
    path('ek-mesai-ekle/<int:mesai_id>/', ek_mesai_views.ek_mesai_ekle, name='ek_mesai_ekle'),
    path('ek-mesai-sil/<int:ek_mesai_id>/', ek_mesai_views.ek_mesai_sil, name='ek_mesai_sil'),

    # Toplu işlemler
    path('toplu-islem/<int:liste_id>/<int:year>/<int:month>/', views.toplu_islem, name='toplu_islem'),
    path('toplu-radyasyon-ata/<int:liste_id>/', views.toplu_radyasyon_ata, name='toplu_radyasyon_ata'),
    path('toplu-sabit-mesai-ata/<int:liste_id>/', views.toplu_sabit_mesai_ata, name='toplu_sabit_mesai_ata'),
    path('toplu-mesai-ata/<int:liste_id>/<int:year>/<int:month>/', views.toplu_mesai_ata, name='toplu_mesai_ata'),
    path('toplu-mesai-degistir/<int:liste_id>/<int:year>/<int:month>/', views.toplu_mesai_degistir, name='toplu_mesai_degistir'),

    # İzin çek
    path('izinleri-mesailere-isle/<int:liste_id>/', views.izinleri_mesailere_isle, name='izinleri_mesailere_isle'),

    # Bildirim işlemleri
    path('bildirimler/', views.bildirimler, name='bildirimler'),
    path('bildirim-onayla/<int:bildirim_id>/', views.bildirim_onayla, name='bildirim_onayla'),
    path('bildirim-sil/<int:bildirim_id>/', views.bildirim_sil, name='bildirim_sil'),
    # path('bildirim-toplu-onay-kaldir/<int:birim_id>/', views.bildirim_toplu_onay_kaldir, name='bildirim_toplu_onay_kaldir'),
    path('bildirim-form/<int:birim_id>/', views.bildirim_form, name='bildirim_form'),
    # path('bildirim-kilit/<int:bildirim_id>/', views.bildirim_kilit, name='bildirim_kilit'),
    # path('bildirim-kilit-ac/<int:bildirim_id>/', views.bildirim_kilit_ac, name='bildirim_kilit_ac'),
    
    # path('bildirim-excel/', views.bildirim_excel, name='bildirim_excel'),
    path('tatil-ekle/', views.tatil_ekle, name='tatil_ekle'),
    path('tatil-duzenle/', views.tatil_duzenle, name='tatil_duzenle'),
    path('tatil-sil/<int:tatil_id>/', views.tatil_sil, name='tatil_sil'),

    # API Endpoints
    path('bildirim/listele/<int:year>/<int:month>/<int:birim_id>/', views.bildirim_listele, name='bildirim_listele'),
    path('bildirim/olustur/', views.bildirim_olustur, name='bildirim_olustur'),
    path('bildirim/toplu-olustur/<int:birim_id>/', views.bildirim_toplu_olustur, name='bildirim_toplu_olustur'),
    path('bildirim/tekil-onay/<int:bildirim_id>/', views.bildirim_tekil_onay, name='bildirim_tekil_onay'),
    path('bildirim/toplu-onay/<int:birim_id>/', views.bildirim_toplu_onay, name='bildirim_toplu_onay'),
    path('bildirim/riskli-sure-guncelle/', views.bildirim_riskli_sure_guncelle, name='bildirim_riskli_sure_guncelle'),
    
    # Riskli Çalışma Yönetimi
    path('riskli-calisma/<int:birim_id>/', riskli_calisma_views.riskli_calisma_yonetim, name='riskli_calisma_yonetim'),
    path('riskli-calisma/kaydet/', riskli_calisma_views.riskli_calisma_kaydet, name='riskli_calisma_kaydet'),

    # Raporlama
    path('raporlama/', views.raporlama, name='raporlama'),
    path('raporlama/excel/', views.export_raporlama_excel, name='export_raporlama_excel'),
    # Raporlama API endpoints
    path('raporlama/update-birim-kodlari-toplu/', views.update_birim_kodlari_toplu, name='update_birim_kodlari_toplu'),
    path('raporlama/kilit-tekil/', views.kilit_tekil, name='kilit_tekil'),
    path('raporlama/kilit-toplu/', views.kilit_toplu, name='kilit_toplu'),
    path('personel-cikar/<int:liste_id>/<int:personel_id>/', views.personel_cikar, name='personel_cikar'),
    path('liste_aciklama_kaydet/', views.liste_aciklama_kaydet, name='liste_aciklama_kaydet'),
    
    # Yönetici Görünümleri
    path('yonetici/birim-listeleri/', views.birim_listeleri, name='birim_listeleri'),
    path('personel-listesi/<int:liste_id>/sira-kaydet/', views.personel_listesi_sira_kaydet, name='personel_listesi_sira_kaydet'),
    path('personel-listesi/<int:liste_id>/onceki-ay-siralamasi/', views.onceki_ay_siralamasi, name='onceki_ay_siralamasi'),

    # İlk Liste Bildirimi
    path('ilk-liste-olustur/<int:liste_id>/', views.ilk_liste_olustur, name='ilk_liste_olustur'),
    path('ilk-liste-onayla/<int:ilk_liste_id>/', views.ilk_liste_onayla, name='ilk_liste_onayla'),
    path('ilk-liste-onay-kaldir/<int:ilk_liste_id>/', views.ilk_liste_onay_kaldir, name='ilk_liste_onay_kaldir'),
    path('ilk-liste-detay/<int:liste_id>/', views.ilk_liste_detay, name='ilk_liste_detay'),

    # Vardiya Dağılımı
    path('vardiya-dagilim/', views.vardiya_dagilim, name='vardiya_dagilim'),
    path('vardiya-dagilim/search/', views.vardiya_dagilim_search, name='vardiya_dagilim_search'),
    path('vardiya-dagilim/kaydet/', views.vardiya_dagilim_kaydet, name='vardiya_dagilim_kaydet'),
    path('vardiya-dagilim/pdf/', views.vardiya_dagilim_pdf, name='vardiya_dagilim_pdf'),
    
    # Günlük İzin Takibi
    path('gunluk-izin-takibi/', views.gunluk_izin_takibi, name='gunluk_izin_takibi'),
    path('gunluk-izin-takibi/search/', views.gunluk_izin_takibi_search, name='gunluk_izin_takibi_search'),
    
    # Çalışma Statüsü Kontrolü
    path('calisma-statusu-list/<int:liste_id>/', views.get_calisma_statusu_list, name='get_calisma_statusu_list'),
    path('calisma-statusu-guncelle/<int:liste_id>/', views.update_calisma_statusu_list, name='update_calisma_statusu_list'),
    
    # Kayseri Entegrasyonu
    path('kayseri-sync-retry/<int:liste_id>/', views.kayseri_sync_retry_view, name='kayseri_sync_retry'),
]

```

---

### Dosya: utils.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\utils.py`

```python
from datetime import date, timedelta, datetime, time
from decimal import Decimal
import calendar
from django.db import models
from .models import ResmiTatil, MazeretKaydi, Mesai, Mesai_Tanimlari, SabitMesai, UserMesaiFavori, YarimZamanliCalisma, EkMesai

def hesapla_fazla_mesai(personel_listesi_kayit, year, month):
    """
    Personel için aylık fazla mesai hesaplar.
    
    Args:
        personel_listesi_kayit: PersonelListesiKayit instance
        year: Yıl
        month: Ay
        
    Returns:
        dict: {
            'olması_gereken_sure': Decimal,
            'fiili_calisma_suresi': Decimal,
            'fazla_mesai': Decimal,
            'calisma_gunleri': int,
            'arefe_gunleri': int,
            'mazeret_azaltimi': Decimal,
            'bayram_fazla_mesai': Decimal,       # Bayram Gündüz
            'normal_fazla_mesai': Decimal,       # Normal Gündüz
            'bayram_gece_fazla_mesai': Decimal,  # Bayram Gece
            'normal_gece_fazla_mesai': Decimal,  # Normal Gece
            'stop_suresi': Decimal,
            'riskli_bayram_fazla_mesai': Decimal,
            'riskli_normal_fazla_mesai': Decimal,
            'riskli_bayram_gece_fazla_mesai': Decimal,
            'riskli_normal_gece_fazla_mesai': Decimal
        }
    """
    personel = personel_listesi_kayit.personel
    radyasyon_calisani = personel_listesi_kayit.radyasyon_calisani
    sabit_mesai = personel_listesi_kayit.sabit_mesai
    is_gunduz_personeli = getattr(personel_listesi_kayit, 'is_gunduz_personeli', True)

    # O dönemdeki yarim_zamanli_calisma durumu
    ilk_gun = date(year, month, 1)
    # Ayın son günü
    days_in_month = calendar.monthrange(year, month)[1]
    son_gun = date(year, month, days_in_month)

    yarim_zamanli_calisma = YarimZamanliCalisma.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=ilk_gun
    ).filter(
        models.Q(bitis_tarihi__isnull=True) | models.Q(bitis_tarihi__gt=ilk_gun)
    ).first()

    if yarim_zamanli_calisma:
        return {
            'olması_gereken_sure': 0,
            'fiili_calisma_suresi': 0,
            'fazla_mesai': 0,
            'calisma_gunleri': 0,
            'arefe_gunleri': 0,
            'mazeret_azaltimi': 0,
            'bayram_fazla_mesai': 0,
            'normal_fazla_mesai': 0,
            'bayram_gece_fazla_mesai': 0,
            'normal_gece_fazla_mesai': 0,
            'stop_suresi': 0,
            'riskli_bayram_fazla_mesai': 0,
            'riskli_normal_fazla_mesai': 0,
            'riskli_bayram_gece_fazla_mesai': 0,
            'riskli_normal_gece_fazla_mesai': 0
        }

    # ==========================================
    # 1. Olması Gereken Süre Hesabı
    # ==========================================
    calisma_gunleri = 0
    arefe_gunleri = 0

    # Resmi tatilleri cache'le (Ay boyu)
    resmi_tatiller_q = ResmiTatil.objects.filter(
        TatilTarihi__year=year,
        TatilTarihi__month=month
    )
    # Tarih -> ArefeMi
    tatil_map_month = {rt.TatilTarihi: rt.ArefeMi for rt in resmi_tatiller_q}

    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        weekday = current_date.weekday()

        if weekday < 5:  # Pazartesi-Cuma
            is_resmi_tatil = current_date in tatil_map_month
            if not is_resmi_tatil:
                calisma_gunleri += 1

            # Arefe kontrolü (ResmiTatil tablosunda varsa)
            if is_resmi_tatil and tatil_map_month[current_date]:
                arefe_gunleri += 1

    gunluk_saat = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
    normal_calisma_suresi = calisma_gunleri * gunluk_saat
    arefe_arttirimi = arefe_gunleri * Decimal('5.0')
    olmasi_gereken_sure = normal_calisma_suresi + arefe_arttirimi

    # ==========================================
    # 2. Fiili Çalışma ve Detaylı Dağılım
    # ==========================================

    # Genişletilmiş Tatil Map (Sarkmalar için +2 gün)
    extended_end = son_gun + timedelta(days=2)
    resmi_tatiller_genis = ResmiTatil.objects.filter(
        TatilTarihi__gte=ilk_gun,
        TatilTarihi__lte=extended_end
    )
    tatil_map_genis = {
        rt.TatilTarihi: {'ArefeMi': rt.ArefeMi, 'BayramMi': rt.BayramMi}
        for rt in resmi_tatiller_genis
    }

    stop_suresi = Decimal('0.0')
    fiili_calisma_suresi = Decimal('0.0')
    izin_azaltimi = Decimal('0.0')

    mesailer = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month
    ).select_related('MesaiTanim').prefetch_related('mercis657_stoplar', 'mercis657_ek_mesailer').order_by('MesaiDate')

    def get_context(dt):
        """Verilen datetime için status döner: is_bayram, is_gece"""
        d = dt.date()
        t = dt.time()

        # Gece: 20:00 - 08:00
        is_gece = (t >= time(20, 0)) or (t < time(8, 0))

        is_bayram = False
        if d in tatil_map_genis:
            info = tatil_map_genis[d]
            arefe_mi = info['ArefeMi']
            bayram_mi = info['BayramMi']

            if arefe_mi:
                # Arefe günü 13:00'den sonra bayram
                if t >= time(13, 0):
                    is_bayram = True
            else:
                if bayram_mi:
                    is_bayram = True

        return is_bayram, is_gece

    # İzin Azaltımı Hesapla (Ortak)
    for mesai in mesailer:
        izin_field = getattr(mesai, 'Izin', None)
        mesai_tarih = getattr(mesai, 'MesaiDate', None)

        if izin_field and mesai_tarih:
            if mesai_tarih.weekday() < 5:  # hafta içi
                is_tatil_gunu = mesai_tarih in tatil_map_month
                if not is_tatil_gunu:
                    per_day = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
                    izin_azaltimi += per_day
                elif tatil_map_month.get(mesai_tarih):
                    izin_azaltimi += Decimal('5.0')

    # 3. Mazeret Hesapla (Ortak - Erken hesaplama gerekli)
    mazeret_azaltimi = Decimal('0.0')
    mazeret_kayitlari = MazeretKaydi.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=son_gun,
        bitis_tarihi__gte=ilk_gun
    )
    for mazeret in mazeret_kayitlari:
        baslangic = max(mazeret.baslangic_tarihi, ilk_gun)
        bitis = min(mazeret.bitis_tarihi, son_gun)
        mazeret_gunleri = 0
        curr = baslangic
        while curr <= bitis:
            if curr.weekday() < 5 and curr not in tatil_map_month:
                izinli_mi = Mesai.objects.filter(Personel=personel, MesaiDate=curr).exclude(Izin=False).exclude(Izin__isnull=True).exists()
                if not izinli_mi:
                    mazeret_gunleri += 1
            curr += timedelta(days=1)
        mazeret_azaltimi += mazeret_gunleri * mazeret.gunluk_azaltim_saat

    # Sabit mesai ara dinlenme toplamı: hafta içi tatil olmayan çalışılan her gün için
    # ara_dinlenme fiili çalışmaya dahildir ama "çalışılması gereken" süreye sayılmaz.
    # Limiti artırarak dengeliyoruz: fazla mesai = fiili - (limit + ara_din_toplam)
    ara_dinlenme_toplam = Decimal('0.0')
    if sabit_mesai and getattr(sabit_mesai, 'ara_dinlenme', None) and sabit_mesai.ara_dinlenme > 0:
        ara_din_per_gun = Decimal(str(sabit_mesai.ara_dinlenme))
        for mesai in mesailer:
            if (
                mesai.MesaiDate.weekday() < 5
                and mesai.MesaiDate not in tatil_map_month
                and not getattr(mesai, 'Izin', None)
                and mesai.MesaiTanim
                and getattr(mesai.MesaiTanim, 'Saat', None)
                and getattr(mesai.MesaiTanim, 'Sure', 0) > 8
            ):
                ara_dinlenme_toplam += ara_din_per_gun

    effective_olmasi_gereken = olmasi_gereken_sure - izin_azaltimi - mazeret_azaltimi + ara_dinlenme_toplam

    # ==========================================
    # YENİ ORTAK HESAPLAMA MANTIĞI
    # ==========================================
    #
    # Tüm mesai segmentleri (stopsuz) tarih sırasına göre işlenir.
    # Her segment şu bilgileri taşır:
    #   - seg_start, seg_end (datetime)
    #   - is_bayram, is_gece (context)
    #   - is_gunduz_08_16: 08:00-16:00 arasında mı?
    #   - duration
    #   - riskli bilgileri
    #
    # Doldurma önceliği:
    #   1. Pass: 08:00-16:00 segmentleri ile effective_olmasi_gereken'i doldur
    #   2. Pass: Kalan limiti diğer segmentlerle (gece + diğer gündüz) doldur
    #
    # Limit dolduktan sonra gelen her segment:
    #   - is_gece → gece fazla mesai (bayram/normal)
    #   - değilse → gündüz fazla mesai (bayram/normal)
    # ==========================================

    # Sabit Mesai Bitiş Saati (Riskli NOBET için)
    sabit_mesai_bitis = None
    if sabit_mesai and sabit_mesai.aralik:
        try:
            parts = sabit_mesai.aralik.strip().split()
            if len(parts) >= 2:
                end_s = parts[1]
                eh, em = map(int, end_s.split(':'))
                sabit_mesai_bitis = time(eh, em)
        except (ValueError, IndexError):
            pass

    # Tüm mesailerden segmentleri çıkar
    all_segments = []  # list of dicts

    for mesai in mesailer:
        if not mesai.MesaiTanim:
            continue

        # Saat tanımlı değilse Sure üzerinden basit segment oluştur (fallback)
        if not mesai.MesaiTanim.Saat:
            if getattr(mesai.MesaiTanim, 'Sure', None):
                sure = Decimal(str(mesai.MesaiTanim.Sure))
                # Fallback: gündüz normal segment kabul et, is_gunduz_08_16=True
                all_segments.append({
                    'seg_start': None,
                    'seg_end': None,
                    'duration': sure,
                    'is_bayram': False,
                    'is_gece': False,
                    'is_gunduz_08_16': True,
                    'mesai': mesai,
                    'risky_duration': sure if mesai.riskli_calisma in (Mesai.RISKLI_TAM, Mesai.RISKLI_NOBET) else Decimal('0.0'),
                })
            continue

        # Mesai aralığını belirle
        try:
            saat_str = mesai.MesaiTanim.Saat.strip()
            start_s, end_s = saat_str.split()
            sh, sm = map(int, start_s.split(':'))
            eh, em = map(int, end_s.split(':'))
            if sh == 24: sh = 0
            if eh == 24: eh = 0
            start_dt = datetime.combine(mesai.MesaiDate, time(sh, sm))
            end_dt = datetime.combine(mesai.MesaiDate, time(eh, em))
            if getattr(mesai.MesaiTanim, 'SonrakiGuneSarkiyor', False) or end_dt <= start_dt:
                end_dt += timedelta(days=1)
        except ValueError:
            continue

        # Stopları belirle
        stops_intervals = []
        stopler = list(mesai.mercis657_stoplar.all())
        for stop in stopler:
            if stop.StopBaslangic and stop.StopBitis:
                sb, se = stop.StopBaslangic, stop.StopBitis
                stop_start_dt = datetime.combine(mesai.MesaiDate, sb)
                if stop_start_dt < start_dt: stop_start_dt += timedelta(days=1)
                stop_end_dt = datetime.combine(mesai.MesaiDate, se)
                if stop_end_dt < stop_start_dt: stop_end_dt += timedelta(days=1)
                stop_start_dt = max(start_dt, stop_start_dt)
                stop_end_dt = min(end_dt, stop_end_dt)
                if stop_end_dt > stop_start_dt:
                    stops_intervals.append((stop_start_dt, stop_end_dt))
                    stop_suresi += Decimal((stop_end_dt - stop_start_dt).total_seconds() / 3600)

        # Timeline milestones: saat sınırları 0, 8, 13, 16, 20
        # Sabit mesai bitiş saati de milestone olarak eklenir
        milestones = set([start_dt, end_dt])
        d_ptr, end_date = start_dt.date(), end_dt.date()
        while d_ptr <= end_date:
            for h in [0, 8, 13, 16, 20]:
                check_dt = datetime.combine(d_ptr, time(h, 0))
                if start_dt < check_dt < end_dt:
                    milestones.add(check_dt)
            if sabit_mesai_bitis:
                sm_dt = datetime.combine(d_ptr, sabit_mesai_bitis)
                if start_dt < sm_dt < end_dt:
                    milestones.add(sm_dt)
            d_ptr += timedelta(days=1)

        sorted_points = sorted(list(milestones))

        for i in range(len(sorted_points) - 1):
            seg_start, seg_end = sorted_points[i], sorted_points[i + 1]
            mid = seg_start + (seg_end - seg_start) / 2

            # Stop içinde mi?
            in_stop = any(s_start <= mid <= s_end for s_start, s_end in stops_intervals)
            if in_stop:
                continue

            duration = Decimal((seg_end - seg_start).total_seconds() / 3600)
            is_bayram, is_gece = get_context(mid)

            # 1. Pass öncelikli segment mi?
            # Sabit mesaisi olan personelde: sabit mesai aralığı (08:00 - sabit_bitis) içinde
            # Sabit mesaisi yoksa: 08:00-16:00 arası (eski mantık)
            seg_start_t = seg_start.time()
            seg_end_t = seg_end.time()
            if sabit_mesai_bitis:
                # Sabit mesai aralığı içinde: bayram değil, sabit bitiş saatinden önce
                is_gunduz_08_16 = (
                    not is_bayram
                    and not is_gece
                    and seg_start_t >= time(8, 0)
                    and seg_end_t <= sabit_mesai_bitis
                    and seg_start_t < seg_end_t
                )
            else:
                # Sabit mesai yok: 08:00-16:00 arası gündüz segmentler
                is_gunduz_08_16 = (
                    not is_bayram
                    and not is_gece
                    and seg_start_t >= time(8, 0)
                    and seg_end_t <= time(16, 0)
                    and seg_start_t < seg_end_t
                )

            # Riskli süre hesabı
            risky_duration = Decimal('0.0')
            if mesai.riskli_calisma == Mesai.RISKLI_TAM:
                risky_duration = duration
            elif mesai.riskli_calisma == Mesai.RISKLI_NOBET:
                if is_gunduz_personeli:
                    # Gündüz personeli: sabit mesai bitişinden sonrası riskli
                    if mesai.MesaiDate.weekday() < 5 and mesai.MesaiDate not in tatil_map_month:
                        if sabit_mesai_bitis:
                            r_start_dt = datetime.combine(mesai.MesaiDate, sabit_mesai_bitis)
                            r_start = max(seg_start, r_start_dt)
                            r_end = seg_end
                            if r_end > r_start:
                                risky_duration = Decimal((r_end - r_start).total_seconds() / 3600)
                else:
                    # Nöbetli personel: vardiyanın tamamı riskli
                    risky_duration = duration

            all_segments.append({
                'seg_start': seg_start,
                'seg_end': seg_end,
                'duration': duration,
                'is_bayram': is_bayram,
                'is_gece': is_gece,
                'is_gunduz_08_16': is_gunduz_08_16,
                'mesai': mesai,
                'risky_duration': risky_duration,
            })

        # ==========================================
        # 3.2. Ek Mesai Segmentleri
        # ==========================================
        for em in mesai.mercis657_ek_mesailer.all():
            try:
                em_start_dt = datetime.combine(mesai.MesaiDate, em.Baslangic)
                em_end_dt = datetime.combine(mesai.MesaiDate, em.Bitis)
                if em_end_dt <= em_start_dt:
                    em_end_dt += timedelta(days=1)
                
                # Ek mesai için de milestone'lara bölerek segment oluştur
                em_milestones = set([em_start_dt, em_end_dt])
                d_ptr, em_end_date = em_start_dt.date(), em_end_dt.date()
                while d_ptr <= em_end_date:
                    for h in [0, 8, 13, 16, 20]:
                        check_dt = datetime.combine(d_ptr, time(h, 0))
                        if em_start_dt < check_dt < em_end_dt:
                            em_milestones.add(check_dt)
                    d_ptr += timedelta(days=1)
                
                em_sorted = sorted(list(em_milestones))
                for j in range(len(em_sorted)-1):
                    es, ee = em_sorted[j], em_sorted[j+1]
                    em_mid = es + (ee - es) / 2
                    em_dur = Decimal((ee - es).total_seconds() / 3600)
                    em_bayram, em_gece = get_context(em_mid)
                    
                    # 08-16 Gündüz mü?
                    es_t, ee_t = es.time(), ee.time()
                    is_gunduz_08_16 = (
                        not em_bayram and not em_gece
                        and es_t >= time(8, 0) and ee_t <= (sabit_mesai_bitis or time(16, 0))
                        and es_t < ee_t
                    )
                    
                    all_segments.append({
                        'seg_start': es,
                        'seg_end': ee,
                        'duration': em_dur,
                        'is_bayram': em_bayram,
                        'is_gece': em_gece,
                        'is_gunduz_08_16': is_gunduz_08_16,
                        'mesai': mesai,
                        'risky_duration': em_dur if em.Riskli else Decimal('0.0'),
                        'is_ek_mesai': True
                    })
            except Exception:
                continue

    # ==========================================
    # Yeni Kronolojik Fazla Mesai Dağıtımı
    # ==========================================

    fiili_calisma_suresi = sum(seg['duration'] for seg in all_segments)
    fazla_mesai = max(Decimal('0.0'), fiili_calisma_suresi - effective_olmasi_gereken)

    # 1. Total Bayram Mesailerini Hesapla
    tot_bayram_gece = Decimal('0.0')
    tot_bayram_gunduz = Decimal('0.0')
    tot_riskli_bayram_gece = Decimal('0.0')
    tot_riskli_bayram_gunduz = Decimal('0.0')

    for seg in all_segments:
        if seg['is_bayram']:
            dur = seg['duration']
            r_dur = seg['risky_duration']
            n_dur = dur - r_dur
            if seg['is_gece']:
                tot_bayram_gece += n_dur
                tot_riskli_bayram_gece += r_dur
            else:
                tot_bayram_gunduz += n_dur
                tot_riskli_bayram_gunduz += r_dur

    total_bayram_worked = tot_bayram_gece + tot_bayram_gunduz + tot_riskli_bayram_gece + tot_riskli_bayram_gunduz

    # Bayram Mesaisi Önceliği
    bayram_ratio = min(Decimal('1.0'), fazla_mesai / total_bayram_worked if total_bayram_worked > 0 else Decimal('1.0'))

    res_bayram_gunduz = tot_bayram_gunduz * bayram_ratio
    res_bayram_gece = tot_bayram_gece * bayram_ratio
    res_riskli_bayram_gunduz = tot_riskli_bayram_gunduz * bayram_ratio
    res_riskli_bayram_gece = tot_riskli_bayram_gece * bayram_ratio

    assigned_bayram = res_bayram_gunduz + res_bayram_gece + res_riskli_bayram_gunduz + res_riskli_bayram_gece
    remaining_ot = fazla_mesai - assigned_bayram

    # Normal Mesailerin Dağılımı: Yeniden Eskiye (Sondan Geriye), aynı vardiya içinde en son saatten geriye doğru
    res_normal_gece = Decimal('0.0')
    res_normal_gunduz = Decimal('0.0')
    res_riskli_normal_gece = Decimal('0.0')
    res_riskli_normal_gunduz = Decimal('0.0')
    
    # Sıralamayı:
    # 1. Mesai tarihi GÜN bazında BÜYÜKTEN KÜÇÜĞE (Yeni -> Eski)
    # 2. Aynı gün içindeki saat dilimleri BÜYÜKTEN KÜÇÜĞE (Geriye doğru, Mesai bitiminden başlangıca)
    sorted_segments_for_allocation = sorted(all_segments, key=lambda s: (
        -(s['mesai'].MesaiDate.toordinal()) if s['mesai'] else (-(s['seg_start'].date().toordinal()) if s['seg_start'] else -999999),
        -(s['seg_start'].timestamp()) if s['seg_start'] else -9999999999
    ))

    # Pass 1: Sadece 16:00-08:00 arasındaki (Standart dışı) verileri kullanarak limit harca
    for seg in sorted_segments_for_allocation:
        if remaining_ot <= 0:
            break
        if seg['is_bayram']:
            continue
        if seg['is_gunduz_08_16']:
            continue # 08:00-16:00 arası standart olanları Pass 1'de alma

        dur = seg['duration']
        if dur <= 0:
            continue
            
        alloc = min(remaining_ot, dur)
        r_ratio = seg['risky_duration'] / dur
        r_alloc = alloc * r_ratio
        n_alloc = alloc - r_alloc
        
        if seg['is_gece']:
            res_normal_gece += n_alloc
            res_riskli_normal_gece += r_alloc
        else:
            res_normal_gunduz += n_alloc
            res_riskli_normal_gunduz += r_alloc
            
        remaining_ot -= alloc

    # Pass 2: Hâlâ limit kalmışsa (tamamı hafta sonu 08-16 olan çok fazla mesai varsa)
    for seg in sorted_segments_for_allocation:
        if remaining_ot <= 0:
            break
        if seg['is_bayram']:
            continue
        if not seg['is_gunduz_08_16']:
            continue # Pass 1'de zaten işlendi

        dur = seg['duration']
        if dur <= 0:
            continue
            
        alloc = min(remaining_ot, dur)
        r_ratio = seg['risky_duration'] / dur
        r_alloc = alloc * r_ratio
        n_alloc = alloc - r_alloc
        
        if seg['is_gece']:
            res_normal_gece += n_alloc
            res_riskli_normal_gece += r_alloc
        else:
            res_normal_gunduz += n_alloc
            res_riskli_normal_gunduz += r_alloc
            
        remaining_ot -= alloc

    return {
        'olması_gereken_sure': olmasi_gereken_sure,
        'fiili_calisma_suresi': fiili_calisma_suresi,
        'fazla_mesai': fazla_mesai,
        'calisma_gunleri': calisma_gunleri,
        'arefe_gunleri': arefe_gunleri,
        'mazeret_azaltimi': mazeret_azaltimi,
        'bayram_fazla_mesai': res_bayram_gunduz,
        'normal_fazla_mesai': res_normal_gunduz,
        'bayram_gece_fazla_mesai': res_bayram_gece,
        'normal_gece_fazla_mesai': res_normal_gece,
        'stop_suresi': stop_suresi,
        'riskli_bayram_fazla_mesai': res_riskli_bayram_gunduz,
        'riskli_normal_fazla_mesai': res_riskli_normal_gunduz,
        'riskli_bayram_gece_fazla_mesai': res_riskli_bayram_gece,
        'riskli_normal_gece_fazla_mesai': res_riskli_normal_gece,
        **hesapla_icap_suresi(personel_listesi_kayit, year, month)
    }

def hesapla_icap_suresi(personel_listesi_kayit, year, month):
    """
    Personel için aylık icap sürelerini hesaplar.
    RFC-009'a göre:
    - Mesai bitişinden ertesi sabah 08:00'e kadar.
    - Hafta sonu/tatil ise tüm gün (veya mesai yoksa 24 saat).
    - Mesai varsa, mesai bitişinden itibaren hesaplanır.
    """
    personel = personel_listesi_kayit.personel
    days_in_month = calendar.monthrange(year, month)[1]
    
    normal_icap = Decimal('0.0')
    bayram_icap = Decimal('0.0')
    icap_detay = {}
    
    # Resmi tatilleri cache'le
    resmi_tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year,
        TatilTarihi__month=month
    )
    tatil_map = {rt.TatilTarihi: rt for rt in resmi_tatiller}

    # İcap kayıtlarını çek
    icap_kayitlari = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month,
        Icap=True
    ).select_related('MesaiTanim')

    for kayit in icap_kayitlari:
        current_date = kayit.MesaiDate
        next_date = current_date + timedelta(days=1)
        
        # Tatil durumlarını belirle
        is_today_bayram = False
        is_today_arefe = False
        is_next_bayram = False
        
        if current_date in tatil_map:
            rt = tatil_map[current_date]
            if rt.BayramMi:
                 is_today_bayram = True
            elif rt.ArefeMi:
                 is_today_arefe = True
        
        # Ertesi günün tatil durumu (cache'den bulunmayabilir, veritabanından çek)
        # Ancak performans için sadece bu ayı cacheledik. Bir sonraki gün bir sonraki aya düşebilir.
        # Basitlik ve performans için tek tek sorgu yerine genişletilmiş cache veya tekil sorgu.
        # Sonraki gün ayın son günü ise sorun yok, sonraki ayın ilk günü ise mapte yok.
        if next_date in tatil_map:
             rt_next = tatil_map[next_date]
             if rt_next.BayramMi:
                 is_next_bayram = True
        else:
             # Ay geçişi kontrolü
             next_rt = ResmiTatil.objects.filter(TatilTarihi=next_date).first()
             if next_rt and next_rt.BayramMi:
                 is_next_bayram = True

        # Zaman dilimleri
        today_08 = datetime.combine(current_date, time(8, 0))
        today_13 = datetime.combine(current_date, time(13, 0))
        today_17 = datetime.combine(current_date, time(17, 0))
        today_24 = datetime.combine(next_date, time(0, 0)) # Bu gece yarısı
        next_08  = datetime.combine(next_date, time(8, 0))
        
        # Başlangıç zamanını belirle (Sabit Kurallar)
        # Hafta içi resmi tatil değilse 17-08 arası
        # Hafta içi Arefeyse 13-08 arası
        # Resmi tatil veya haftasonuysa 24 saat (08-08)
        
        is_weekend = current_date.weekday() >= 5
        is_resmi_tatil = current_date in tatil_map
        
        if is_weekend:
            start_dt = today_08
        elif is_resmi_tatil:
            rt = tatil_map[current_date]
            if rt.ArefeMi:
                start_dt = today_13
            else:
                start_dt = today_08
        else:
            start_dt = today_17

        # Bitiş zamanı her zaman ertesi gün 08:00
        end_dt = next_08
        
        if start_dt >= end_dt:
             continue # Geçersiz aralık

        # Süre hesaplama ve dağıtma
        current_cursor = start_dt
        day_bayram_sum = Decimal('0.0')
        day_normal_sum = Decimal('0.0')

        # Kritik eşikler: 13:00 (Arefe), 24:00 (Gece geçişi)
        check_points = sorted([t for t in [today_13, today_24] if current_cursor < t < end_dt])
        # Bitiş noktasını da ekle
        points = check_points + [end_dt]
        
        for p in points:
            if current_cursor >= p:
                continue
            
            segment_duration = Decimal((p - current_cursor).total_seconds() / 3600)
            
            # Bu segmentin türünü belirle
            is_segment_bayram = False
            
            # Period: current_cursor -> p
            mid_point = current_cursor + (p - current_cursor) / 2
            
            # 1. Bugünün kontrolü (08:00 - 24:00 arası)
            if mid_point < today_24:
                if is_today_bayram:
                    is_segment_bayram = True
                elif is_today_arefe:
                    # 13:00 sonrası bayram
                    if mid_point >= today_13:
                        is_segment_bayram = True
                    else:
                        is_segment_bayram = False
                else:
                    is_segment_bayram = False
            # 2. Yarının kontrolü (00:00 - 08:00 arası)
            else:
                if is_next_bayram:
                    is_segment_bayram = True
                else:
                     # Sonraki gün bayram değilse normal icap
                     is_segment_bayram = False
            
            if is_segment_bayram:
                day_bayram_sum += segment_duration
            else:
                day_normal_sum += segment_duration
                
            current_cursor = p
            
        bayram_icap += day_bayram_sum
        normal_icap += day_normal_sum
            
        # Format: 'YYYY-MM-DD' key for the notification detail
        key = current_date.strftime('%Y-%m-%d')
        icap_detay[key] = float(day_bayram_sum + day_normal_sum) # Toplam süreyi yazıyoruz detay olarak

    return {
        'normal_icap': normal_icap,
        'bayram_icap': bayram_icap,
        'toplam_icap': normal_icap + bayram_icap,
        'icap_detay': icap_detay
    }

def get_favori_mesailer(user):
    """Kullanıcının favori mesailerini döndürür. Favori yoksa tüm mesailer gelir."""
    favoriler = UserMesaiFavori.objects.filter(user=user).select_related("mesai").order_by("mesai")
    if favoriler.exists():
        return [f.mesai for f in favoriler]
    return Mesai_Tanimlari.objects.all().order_by("Saat")


def hesapla_fazla_mesai_sade(personel_listesi_kayit, year, month):
    """
    Sadeleştirilmiş fazla mesai hesaplama (bayram mesaisi hariç).
    Anlık hesaplama için kullanılır.
    
    Args:
        personel_listesi_kayit: PersonelListesiKayit instance
        year: Yıl
        month: Ay
        
    Returns:
        Decimal: Fazla mesai değeri (saat cinsinden)
    """
    personel = personel_listesi_kayit.personel
    radyasyon_calisani = personel_listesi_kayit.radyasyon_calisani
    sabit_mesai = personel_listesi_kayit.sabit_mesai
    
    # Yarım zamanlı çalışma kontrolü
    ilk_gun = date(year, month, 1)
    yarim_zamanli_calisma = YarimZamanliCalisma.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=ilk_gun
    ).filter(
        models.Q(bitis_tarihi__isnull=True) | models.Q(bitis_tarihi__gt=ilk_gun)
    ).first()

    if yarim_zamanli_calisma:
        return Decimal('0.0')

    # Aylık gün sayısı ve hafta içi günleri hesapla
    days_in_month = calendar.monthrange(year, month)[1]
    calisma_gunleri = 0
    arefe_gunleri = 0

    # Resmi tatilleri al
    resmi_tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year,
        TatilTarihi__month=month
    )
    
    # Hafta içi günleri say
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        weekday = current_date.weekday()

        if weekday < 5:  # Pazartesi-Cuma
            is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=current_date).exists()
            if not is_resmi_tatil:
                calisma_gunleri += 1

            is_arefe = resmi_tatiller.filter(
                TatilTarihi=current_date,
                ArefeMi=True
            ).exists()
            if is_arefe:
                arefe_gunleri += 1
    
    # Günlük çalışma saati
    gunluk_saat = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')

    # Olması gereken süre hesapla
    normal_calisma_suresi = calisma_gunleri * gunluk_saat
    arefe_arttirimi = arefe_gunleri * Decimal('5.0')
    olmasi_gereken_sure = normal_calisma_suresi + arefe_arttirimi

    # Fiili çalışma süresini hesapla
    fiili_calisma_suresi = Decimal('0.0')

    # O ayki mesai kayıtlarını al
    mesailer = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month
    ).select_related('MesaiTanim').prefetch_related('mercis657_stoplar', 'mercis657_ek_mesailer')

    # İzin kaynaklı azaltım
    izin_azaltimi = Decimal('0.0')
    stop_suresi = Decimal('0.0')

    for mesai in mesailer:
        # Fiili çalışma süresine ekleme
        if mesai.MesaiTanim and getattr(mesai.MesaiTanim, 'Sure', None):
            if sabit_mesai and mesai.MesaiTanim.Sure > 8 and mesai.MesaiDate.weekday() < 5:
                fiili_calisma_suresi -= sabit_mesai.ara_dinlenme
            fiili_calisma_suresi += mesai.MesaiTanim.Sure

        # STOP sürelerini düş
        stopler = list(getattr(mesai, 'mercis657_stoplar').all())
        for stop in stopler:
            try:
                stop_hours = Decimal(str(stop.Sure)) if stop.Sure is not None else Decimal('0.0')
            except Exception:
                stop_hours = Decimal('0.0')
            fiili_calisma_suresi -= stop_hours
            stop_suresi += stop_hours

        # Ek Mesai sürelerini ekle
        ek_mesailer = list(getattr(mesai, 'mercis657_ek_mesailer').all())
        for ek in ek_mesailer:
            try:
                ek_hours = Decimal(str(ek.Sure)) if ek.Sure is not None else Decimal('0.0')
            except Exception:
                ek_hours = Decimal('0.0')
            fiili_calisma_suresi += ek_hours

        # İzin azaltımı
        izin_field = getattr(mesai, 'Izin', None)
        mesai_tarih = getattr(mesai, 'MesaiDate', None)
        if izin_field and mesai_tarih:
            if mesai_tarih.weekday() < 5:  # hafta içi
                is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=mesai_tarih).exists()
                if not is_resmi_tatil:
                    per_day = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
                    izin_azaltimi += per_day
                else:
                    is_arefe = resmi_tatiller.filter(TatilTarihi=mesai_tarih, ArefeMi=True).exists()
                    if is_arefe:
                        izin_azaltimi += Decimal('5.0')

    # Mazeret azaltımını hesapla
    mazeret_azaltimi = Decimal('0.0')
    mazeret_kayitlari = MazeretKaydi.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=date(year, month, days_in_month),
        bitis_tarihi__gte=date(year, month, 1)
    )

    for mazeret in mazeret_kayitlari:
        baslangic = max(mazeret.baslangic_tarihi, date(year, month, 1))
        bitis = min(mazeret.bitis_tarihi, date(year, month, days_in_month))

        mazeret_gunleri = 0
        current_date = baslangic
        while current_date <= bitis:
            if current_date.weekday() < 5:  # Hafta içi
                is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=current_date).exists()
                if not is_resmi_tatil:
                    izinli_mi = Mesai.objects.filter(
                        Personel=personel,
                        MesaiDate=current_date
                    ).exclude(Izin=False).exclude(Izin__isnull=True).exists()
                    if not izinli_mi:
                        mazeret_gunleri += 1
            current_date += timedelta(days=1)

        mazeret_azaltimi += mazeret_gunleri * mazeret.gunluk_azaltim_saat

    # Mazeret azaltımı fiili çalışma süresine ekleniyor
    # fiili_calisma_suresi += mazeret_azaltimi

    # İzin azaltımını olması gereken süreden düş
    olmasi_gereken_sure -= (izin_azaltimi + mazeret_azaltimi)

    # Fazla mesai hesapla
    fazla_mesai = fiili_calisma_suresi - olmasi_gereken_sure

    return fazla_mesai


def get_vardiya_tanimlari():
    """
    Tüm mesai tanımlarının vardiya bilgilerini döndürür.
    
    Returns:
        dict: { mesai_id: { 'gunduz': bool, 'aksam': bool, 'gece': bool } }
    """
    mesai_tanimlari = Mesai_Tanimlari.objects.all()
    result = {}
    for mt in mesai_tanimlari:
        result[mt.id] = {
            'gunduz': mt.GunduzMesaisi,
            'aksam': mt.AksamMesaisi,
            'gece': mt.GeceMesaisi
        }
    return result

def get_turkish_month_name(month_index):
    """
    Ay indeksine göre Türkçe ay ismini döndürür.
    1 -> Ocak
    """
    months = [
        "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
    ]
    try:
        m = int(month_index)
        if 1 <= m <= 12:
            return f"{months[m]} Ayı"
    except (ValueError, TypeError):
        pass
    return f"{month_index}. Dönem"

def hesapla_riskli_calisma(personel_listesi_kayit, year, month):
    """
    Personel için toplam riskli çalışma süresini hesaplar (hesapla_fazla_mesai fonksiyonunu kullanır).
    """
    sonuc = hesapla_fazla_mesai(personel_listesi_kayit, year, month)
    total = (
        sonuc.get('riskli_bayram_fazla_mesai', Decimal('0.0')) +
        sonuc.get('riskli_normal_fazla_mesai', Decimal('0.0')) +
        sonuc.get('riskli_bayram_gece_fazla_mesai', Decimal('0.0')) +
        sonuc.get('riskli_normal_gece_fazla_mesai', Decimal('0.0'))
    )
    return total

def duzelt_icap_kayitlari(donem_baslangic):
    """
    Belirtilen dönemdeki tüm bildirimler için icap sürelerini yeniden hesaplar ve günceller.
    Değişen kayıtları raporlar ve excel çıktısı üretir.
    
    Args:
        donem_baslangic (str or date): 'YYYY-MM-DD' formatında string veya date objesi.
    """
    from .models import Bildirim, PersonelListesiKayit
    import pandas as pd
    
    if isinstance(donem_baslangic, str):
        target_date = datetime.strptime(donem_baslangic, '%Y-%m-%d').date()
    else:
        target_date = donem_baslangic

    bildirimler = Bildirim.objects.filter(DonemBaslangic=target_date)
    
    updated_records = []
    total_count = bildirimler.count()
    change_count = 0
    scanned_count = 0
    
    print(f"Toplam {total_count} bildirim incelenecek. Dönem: {target_date}")

    for b in bildirimler:
        scanned_count += 1
        
        # PersonelListesiKayit bul
        plk = PersonelListesiKayit.objects.filter(
            liste=b.PersonelListesi,
            personel=b.Personel
        ).first()
        
        if not plk:
            print(f"Kayıt bulunamadı: {b.Personel} - {b.PersonelListesi}")
            continue
            
        # Icap Hesaplama
        sonuc = hesapla_icap_suresi(plk, target_date.year, target_date.month)
        
        yeni_normal = sonuc['normal_icap']
        yeni_bayram = sonuc['bayram_icap']
        yeni_detay = sonuc['icap_detay']
        
        # Değişiklik Kontrolü
        diff = False
        
        # Decimal karşılaştırma
        if abs(b.NormalIcap - yeni_normal) > Decimal('0.01'):
            diff = True
        elif abs(b.BayramIcap - yeni_bayram) > Decimal('0.01'):
            diff = True
        # Detay kontrolü (basit string/json comparison)
        elif b.IcapDetay != yeni_detay:
             diff = True

        if diff:
            old_normal = b.NormalIcap
            old_bayram = b.BayramIcap
            
            b.NormalIcap = yeni_normal
            b.BayramIcap = yeni_bayram
            b.IcapDetay = yeni_detay
            b.save()
            
            change_count += 1
            updated_records.append({
                'Personel': f"{b.Personel.PersonelName} {b.Personel.PersonelSurname}",
                'Eski Normal Icap': float(old_normal),
                'Yeni Normal Icap': float(yeni_normal),
                'Eski Bayram Icap': float(old_bayram),
                'Yeni Bayram Icap': float(yeni_bayram)
            })
            
    print(f"İşlem Tamamlandı.")
    print(f"İncelenen Kayıt Sayısı: {scanned_count}")
    print(f"Değişen Kayıt Sayısı: {change_count}")
    
    if updated_records:
        try:
            df = pd.DataFrame(updated_records)
            output_file = f"icap_duzeltme_raporu_{target_date}.xlsx"
            df.to_excel(output_file, index=False)
            print(f"Excel raporu oluşturuldu: {output_file}")
            return output_file
        except Exception as e:
            print(f"Excel raporu oluşturulurken hata: {e}")
            return None
    else:
        print("Herhangi bir değişiklik yapılmadı.")
        return None
```

---

### Dosya: valuelists.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\valuelists.py`

```python
CKYS_BTF_VALUES = [
    "08_16",
    "08_18",
    "08_20",
    "08_24",
    "08_08",
    "08_13",
    "16_24",
    "16_08",
    "20_08",
    "24_08",
    "7 SAAT"
]
```

---

### Dosya: views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views.py`

```python

```

---

### Dosya: __init__.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\__init__.py`

```python

```

---

### Dosya: management\__init__.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\management\__init__.py`

```python

```

---

### Dosya: management\commands\sync_izinler.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\management\commands\sync_izinler.py`

```python
import os
import json
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime, date, timedelta
from mercis657.models import Mesai, Personel, Izin
from PersonelYonSis.FMConnection.KDHIzin import IzinSorgula

def get_or_create_izin_turu(izin_adi):
    izin_obj, created = Izin.objects.get_or_create(
        fm_karsiligi=izin_adi,
        defaults={'ad': izin_adi}
    )
    return izin_obj

class Command(BaseCommand):
    help = 'Mevcut tarihten 30 gün öncesi ve sonrası için FileMaker üzerinden izinleri çekip Mesai tablosuna işler.'

    def handle(self, *args, **kwargs):
        today = date.today()
        baslangic = today - timedelta(days=30)
        bitis = today + timedelta(days=30)
        
        self.stdout.write(f"İzinler çekiliyor: {baslangic} - {bitis}...")
        
        try:
            izinler = IzinSorgula(
                baslangic=baslangic.strftime("%Y-%m-%d"),
                bitis=bitis.strftime("%Y-%m-%d")
            )
            
            if not izinler:
                self.stdout.write(self.style.WARNING("Belirtilen tarih aralığında izin bulunamadı."))
                return

            updated_count = 0
            
            # Veritabanı gecikmesini önlemek için tüm personeli çekelim
            personel_qs = Personel.objects.all()
            personel_map = {}
            for p in personel_qs:
                if p.PersonelTCKN:
                    # FileMaker'dan string veya number gelebilir
                    personel_map[str(p.PersonelTCKN)] = p
            
            for row in izinler:
                tckn, baslangic_tarihi, bitis_tarihi, izin_turu = row
                
                personel = personel_map.get(str(tckn))
                if not personel:
                    continue  # Sistemimizde olmayan bir personel ise atla
                
                # İzin türü objesini getir
                izin_obj = get_or_create_izin_turu(izin_turu)
                
                try:
                    start_date = datetime.strptime(str(baslangic_tarihi), "%Y-%m-%d").date()
                    # İzin bitiş günü dahil edilmediği için (genellikle FileMaker'da böyledir) 1 gün çıkarılıyor
                    end_date = datetime.strptime(str(bitis_tarihi), "%Y-%m-%d").date() - timedelta(days=1)
                except ValueError:
                    continue
                
                # Bu tarih aralığındaki Mesai kayıtlarını bul
                mesailer = Mesai.objects.filter(
                    Personel=personel,
                    MesaiDate__range=(start_date, end_date)
                )

                for mesai in mesailer:
                    if mesai.Izin != izin_obj:
                        mesai.Izin = izin_obj
                        mesai.SistemdekiIzin = True
                        mesai.MesaiTanim = None  # İzinli günde mesai olmaz
                        mesai.save(update_fields=["Izin", "MesaiTanim", "SistemdekiIzin"])
                        updated_count += 1
                    elif mesai.Izin == izin_obj and not mesai.SistemdekiIzin:
                        mesai.SistemdekiIzin = True
                        mesai.save(update_fields=["SistemdekiIzin"])
                        updated_count += 1
                        
            # Son güncellenme verisini dosyaya yaz
            sync_file_path = os.path.join(settings.BASE_DIR, 'mercis657', 'last_izin_sync.json')
            sync_data = {
                'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'count': updated_count
            }
            try:
                with open(sync_file_path, 'w', encoding='utf-8') as f:
                    json.dump(sync_data, f)
            except Exception as file_exp:
                self.stdout.write(self.style.WARNING(f"Log dosyası yazılamadı: {str(file_exp)}"))

            self.stdout.write(self.style.SUCCESS(f"Başarıyla {updated_count} mesai kaydı güncellendi."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"İşlem sırasında hata oluştu: {str(e)}"))

```

---

### Dosya: management\commands\__init__.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\management\commands\__init__.py`

```python

```

---

### Dosya: templatetags\mercis_filters.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\templatetags\mercis_filters.py`

```python
from django import template

register = template.Library()

@register.filter
def dot_decimal(value):
    """Virgülleri noktaya çevirir"""
    if value is None:
        return ""
    return str(value).replace(",", ".")

@register.filter
def get_item(dictionary, key):
    """Güvenli dict.get kullanımı"""
    try:
        if dictionary is None:
            return None
        return dictionary.get(key)
    except Exception:
        return None
```

---

### Dosya: templatetags\__init__.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\templatetags\__init__.py`

```python

```

---

### Dosya: views\bildirim_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\bildirim_views.py`

```python
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string, get_template
import pdfkit
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib import messages
from django.conf import settings
import re
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Bildirim, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin, EkMesai
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from mercis657.utils import hesapla_fazla_mesai, get_turkish_month_name


def get_donemler():
    """Mevcut aydan -6 ay ile +2 ay arası dönem listesi"""
    today = date.today().replace(day=1)
    donemler = []
    for i in range(-6, 3):
        d = today + relativedelta(months=i)
        value = f"{d.year}/{d.month:02d}"
        label = f"{d.month:02d}/{d.year}" # Görüntülenecek format
        donemler.append({'value': value, 'label': label})
    return donemler


@login_required
def bildirimler(request):
    """Mesai ve İcap bildirimlerini birleşik görüntüler"""
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
        return HttpResponseForbidden("Yetkiniz yok.")

    selected_donem = request.GET.get("donem")
    if not selected_donem:
        today = date.today().replace(day=1)
        selected_donem = f"{today.year}/{today.month:02d}"

    year, month = map(int, selected_donem.split("/"))
    donem_baslangic = date(year, month, 1)

    # Yetki kontrolü ve Birimlerin listelenmesi
    tum_birimler_yetkisi = request.user.has_permission("ÇS 657 Tüm Birimleri Görebilir")
    user_birim_ids = list(UserBirim.objects.filter(user=request.user).values_list('birim__BirimID', flat=True))

    if tum_birimler_yetkisi:
        # Tüm birimleri gör (Kurum, UstBirim, Idareci bilgileriyle)
        birimler = Birim.objects.select_related('Kurum', 'UstBirim', 'Idareci').all().order_by('BirimAdi')
    else:
        # Sadece yetkili olduğu birimleri gör
        birimler = Birim.objects.filter(BirimID__in=user_birim_ids).select_related('Kurum', 'UstBirim', 'Idareci').order_by('BirimAdi')

    selected_birim_id = request.GET.get("birim_id")
    selected_birim = None
    
    if selected_birim_id:
        try:
            bid = int(selected_birim_id)
            # Eğer tümünü görme yetkisi varsa veya kullanıcı bu birimde yetkili ise
            if tum_birimler_yetkisi or (bid in user_birim_ids):
                selected_birim = get_object_or_404(Birim, BirimID=bid)
        except ValueError:
            pass
            
    if not selected_birim and birimler.exists():
        selected_birim = birimler.first() # Varsayılan olarak listedeki ilk birimi seç
    
    personel_data_for_template = []

    if selected_birim:
        # Seçilen döneme ve birime ait PersonelListesi'ni bul
        personel_listesi_obj = PersonelListesi.objects.filter(
            birim=selected_birim, yil=year, ay=month
        ).first()

        if personel_listesi_obj:
            # PersonelListesi'ndeki tüm personelleri al
            personel_kayitlari = PersonelListesiKayit.objects.filter(liste=personel_listesi_obj).select_related('personel')
            personeller_in_list = [pk.personel for pk in personel_kayitlari]

            # Her personel için Bildirim verilerini topla
            for personel in personeller_in_list:
                bildirim = Bildirim.objects.filter(
                    PersonelListesi=personel_listesi_obj,
                    DonemBaslangic=donem_baslangic,
                    SilindiMi=False,
                ).first() # Personel listesi ve dönem başlangıcına göre bildirim
                
                daily_mesai_detay = {}
                daily_icap_detay = {}
                total_normal_fazla_mesai = 0
                total_bayram_fazla_mesai = 0
                total_riskli_normal_fazla_mesai = 0
                total_riskli_bayram_fazla_mesai = 0
                total_normal_icap = 0
                total_bayram_icap = 0
                onay_durumu = 0
                onaylayan_kullanici = None
                onay_tarihi = None
                bildirim_id = None
                calisma_gunleri = 0

                if bildirim:
                    bildirim_id = bildirim.BildirimID
                    onay_durumu = bildirim.OnayDurumu
                    onaylayan_kullanici = bildirim.OnaylayanKullanici
                    onay_tarihi = bildirim.OnayTarihi
                    
                    total_normal_fazla_mesai = bildirim.NormalFazlaMesai
                    total_bayram_fazla_mesai = bildirim.BayramFazlaMesai
                    total_riskli_normal_fazla_mesai = bildirim.RiskliNormalFazlaMesai
                    total_riskli_bayram_fazla_mesai = bildirim.RiskliBayramFazlaMesai
                    total_normal_icap = bildirim.NormalIcap
                    total_bayram_icap = bildirim.BayramIcap

                    if bildirim.MesaiDetay: # JSONField olduğu için kontrol et
                        daily_mesai_detay = {date_str: hours for date_str, hours in bildirim.MesaiDetay.items()}
                    if bildirim.IcapDetay:
                        daily_icap_detay = {date_str: hours for date_str, hours in bildirim.IcapDetay.items()}
                    calisma_gunleri = len(daily_mesai_detay) # Örnek: MesaiDetay dolu gün sayısı

                personel_data_for_template.append({
                    'personel': personel,
                    'bildirim_id': bildirim_id,
                    'normal_fazla_mesai': total_normal_fazla_mesai,
                    'bayram_fazla_mesai': total_bayram_fazla_mesai,
                    'riskli_normal_fazla_mesai': total_riskli_normal_fazla_mesai,
                    'riskli_bayram_fazla_mesai': total_riskli_bayram_fazla_mesai,
                    'toplam_fazla_mesai': total_normal_fazla_mesai + total_bayram_fazla_mesai + 
                                          total_riskli_normal_fazla_mesai + total_riskli_bayram_fazla_mesai,
                    'normal_icap': total_normal_icap,
                    'bayram_icap': total_bayram_icap,
                    'toplam_icap': total_normal_icap + total_bayram_icap,
                    'calisma_gunleri': calisma_gunleri,
                    'onay_durumu': onay_durumu,
                    'onaylayan_kullanici': onaylayan_kullanici,
                    'onay_tarihi': onay_tarihi,
                    'daily_mesai_detay': daily_mesai_detay,
                    'daily_icap_detay': daily_icap_detay,
                })
        
    # Ayın günlerini hazırla
    num_days = calendar.monthrange(year, month)[1]
    days = []
    for day_num in range(1, num_days + 1):
        current_date = date(year, month, day_num)
        is_weekend = current_date.weekday() >= 5  # Cumartesi (5) veya Pazar (6)
        is_holiday = False # ResmiTatil modelinden kontrol edilebilir
        days.append({
            'day_num': day_num,
            'full_date': current_date.strftime("%Y-%m-%d"),
            'is_weekend': is_weekend,
            'is_holiday': is_holiday,
        })
    
    # Yetki kontrolünü context'e ekle
    can_approve_notifications = request.user.has_permission("ÇS 657 Bildirim Onaylama")
    print ("", can_approve_notifications)
    context = {
        "donemler": get_donemler(),
        "selected_donem": selected_donem,
        "birimler": birimler,
        "selected_birim": selected_birim,
        "personel_data": personel_data_for_template,
        "days": days,
        "current_month_label": calendar.month_name[month], # Ay adını şablonda göstermek için
        "current_year": year,
        "can_approve_notifications": can_approve_notifications,
    }
    return render(request, "mercis657/bildirimler.html", context)

@login_required
def bildirim_onayla(request, bildirim_id):
    """Bildirimi onayla"""
    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if not request.user.has_permission("ÇS 657 Bildirim Onaylama"):
        return HttpResponseForbidden("Yetkiniz yok.")

    if bildirim.OnayDurumu == 1:
        messages.warning(request, "Bildirim zaten onaylanmış.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")

    bildirim.OnayDurumu = 1
    bildirim.OnaylayanKullanici = request.user
    bildirim.OnayTarihi = date.today() # datetime.now() olarak güncellenebilir
    bildirim.save()

    messages.success(request, "Bildirim başarıyla onaylandı.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")


@login_required
def bildirim_sil(request, bildirim_id):
    """Bildirimi soft delete yap"""
    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
        return HttpResponseForbidden("Yetkiniz yok.")

    if bildirim.OnayDurumu == 1:
        messages.error(request, "Onaylanmış bildirim silinemez.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")


    bildirim.SilindiMi = True
    bildirim.save()
    messages.success(request, "Bildirim başarıyla silindi.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")

@login_required
def bildirim_listele(request, year, month, birim_id):
    """Return JSON list of bildirim data for given year, month and birim."""
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    try:
        year = int(year); month = int(month)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz tarih.'}, status=400)

    birim = Birim.objects.filter(BirimID=birim_id).first()
    if not birim:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
    if not liste:
        return JsonResponse({'status': 'success', 'data': []})

    donem_baslangic = date(year, month, 1)
    result = []

    # preload Mesai and ResmiTatil
    from ..models import ResmiTatil as RT
    tatiller = RT.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
    tatil_days = [t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM']

    personel_kayitlari = liste.kayitlar.select_related('personel').all()
    for kayit in personel_kayitlari:
        p = kayit.personel
        bildirim = Bildirim.objects.filter(Personel=p, DonemBaslangic=donem_baslangic, SilindiMi=False).first()

        # defaults
        normal = bayram = rnormal = rbayram = nicap = bicap = 0
        mesai_detay = {}
        icap_detay = {}
        onay_durumu = 0
        mutemet_kilit = False
        bildirim_id = None

        if bildirim:
            bildirim_id = bildirim.BildirimID
            normal = float(bildirim.NormalFazlaMesai)
            bayram = float(bildirim.BayramFazlaMesai)
            rnormal = float(bildirim.RiskliNormalFazlaMesai)
            rbayram = float(bildirim.RiskliBayramFazlaMesai)
            
            # Gece değerleri
            gnormal = float(bildirim.GeceNormalFazlaMesai)
            gbayram = float(bildirim.GeceBayramFazlaMesai)
            grnormal = float(bildirim.GeceRiskliNormalFazlaMesai)
            grbayram = float(bildirim.GeceRiskliBayramFazlaMesai)
            
            nicap = float(bildirim.NormalIcap)
            bicap = float(bildirim.BayramIcap)
            mesai_detay = bildirim.MesaiDetay or {}
            icap_detay = bildirim.IcapDetay or {}
            onay_durumu = int(bildirim.OnayDurumu or 0)
            mutemet_kilit = bool(bildirim.MutemetKilit)
        else:
             # Değişkenlerin tanımlı olduğundan emin ol
             gnormal = gbayram = grnormal = grbayram = 0.0

        result.append({
            'personel_id': p.PersonelID,
            'personel_name': p.PersonelName + ' ' + p.PersonelSurname,
            'bildirim_id': bildirim_id,
            'normal_mesai': normal,
            'bayram_mesai': bayram,
            'riskli_normal': rnormal,
            'riskli_bayram': rbayram,
            'gece_normal_mesai': gnormal,
            'gece_bayram_mesai': gbayram,
            'gece_riskli_normal': grnormal,
            'gece_riskli_bayram': grbayram,
            'toplam_mesai': normal + bayram + rnormal + rbayram + gnormal + gbayram + grnormal + grbayram,
            'normal_icap': nicap,
            'bayram_icap': bicap,
            'toplam_icap': nicap + bicap,
            'MesaiDetay': mesai_detay,
            'IcapDetay': icap_detay,
            'onay_durumu': onay_durumu,
            'mutemet_kilit': mutemet_kilit,
        })

    return JsonResponse({'status': 'success', 'data': result})


@login_required
@require_POST
def bildirim_olustur(request):
    """Create or update a single bildirim for a person (expects JSON).
    Body: { personel_id, birim_id, donem: 'YYYY/MM' }
    Returns bildirim_data suitable for JS updateSingleBildirimRow
    """
    try:
        if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
            return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

        try:
            data = json.loads(request.body)
            personel_id = int(data.get('personel_id'))
            birim_id = int(data.get('birim_id'))
            donem = data.get('donem')
            if not (personel_id and birim_id and donem):
                return JsonResponse({'status': 'error', 'message': 'Eksik parametre.'}, status=400)
            year, month = map(int, donem.split('/') if '/' in donem else donem.split('-'))
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'}, status=400)

        birim = Birim.objects.filter(BirimID=birim_id).first()
        if not birim:
            return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

        liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
        if not liste:
            return JsonResponse({'status': 'error', 'message': 'Personel listesi bulunamadı.'}, status=404)

        personel = Personel.objects.filter(PersonelID=personel_id).first()
        if not personel:
            return JsonResponse({'status': 'error', 'message': 'Personel bulunamadı.'}, status=404)

        donem_baslangic = date(year, month, 1)

        # Build MesaiDetay and IcapDetay from Mesai entries
        mesai_qs = Mesai.objects.filter(Personel=personel, MesaiDate__year=year, MesaiDate__month=month).select_related('MesaiTanim', 'Izin')
        mesai_detay = {}
        icap_detay = {}
        
        # PersonelListesiKayit'ı bul
        personel_listesi_kayit = liste.kayitlar.filter(personel=personel).first()
        if not personel_listesi_kayit:
            return JsonResponse({'status': 'error', 'message': 'Personel listesi kaydı bulunamadı.'}, status=404)

        # Hesaplama fonksiyonunu çağır
        fazla_mesai_sonuclari = hesapla_fazla_mesai(personel_listesi_kayit, year, month)

        normal = fazla_mesai_sonuclari.get('normal_fazla_mesai', Decimal('0.0'))
        bayram = fazla_mesai_sonuclari.get('bayram_fazla_mesai', Decimal('0.0'))
        
        # Gece Değerleri
        gnormal = fazla_mesai_sonuclari.get('normal_gece_fazla_mesai', Decimal('0.0'))
        gbayram = fazla_mesai_sonuclari.get('bayram_gece_fazla_mesai', Decimal('0.0'))
        
        rnormal = fazla_mesai_sonuclari.get('riskli_normal_fazla_mesai', Decimal('0.0'))
        rbayram = fazla_mesai_sonuclari.get('riskli_bayram_fazla_mesai', Decimal('0.0'))
        grnormal = fazla_mesai_sonuclari.get('riskli_normal_gece_fazla_mesai', Decimal('0.0'))
        grbayram = fazla_mesai_sonuclari.get('riskli_bayram_gece_fazla_mesai', Decimal('0.0'))

        # Radyasyon çalışanları için NORMAL mesaileri de riskli grubuna kaydır
        if personel_listesi_kayit.radyasyon_calisani:
            rnormal += normal
            rbayram += bayram
            grnormal += gnormal
            grbayram += gbayram
            
            normal = Decimal('0.0')
            bayram = Decimal('0.0')
            gnormal = Decimal('0.0')
            gbayram = Decimal('0.0')
        
        nicap = fazla_mesai_sonuclari.get('normal_icap', Decimal('0.0'))
        bicap = fazla_mesai_sonuclari.get('bayram_icap', Decimal('0.0'))
        
        icap_detay_data = fazla_mesai_sonuclari.get('icap_detay', {})
        if icap_detay_data:
             icap_detay = icap_detay_data
        
        # load resmi tatiller
        tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
        # tatil_days = [t.TatilTarihi for t in tatiller if t.TatilTipi == 'TAM'] # Artık buna gerek yok

        for m in mesai_qs:
            key = m.MesaiDate.strftime('%Y-%m-%d')
            if m.Izin:
                mesai_detay[key] = {'izin': m.Izin.ad}
            elif m.MesaiTanim:
                mesai_detay[key] = {'saat': m.MesaiTanim.Saat}

        # Create or update Bildirim
        with transaction.atomic():
            bildirim, created = Bildirim.objects.get_or_create(
                Personel=personel,
                DonemBaslangic=donem_baslangic,
                defaults={
                    'PersonelListesi': liste,
                    'OlusturanKullanici': request.user,
                    'MesaiDetay': mesai_detay,
                    'IcapDetay': icap_detay,
                    'NormalFazlaMesai': normal,
                    'BayramFazlaMesai': bayram,
                    'RiskliNormalFazlaMesai': rnormal,
                    'RiskliBayramFazlaMesai': rbayram,
                    'GeceNormalFazlaMesai': gnormal,
                    'GeceBayramFazlaMesai': gbayram,
                    'GeceRiskliNormalFazlaMesai': grnormal,
                    'GeceRiskliBayramFazlaMesai': grbayram,
                    'NormalIcap': nicap,
                    'BayramIcap': bicap,
                }
            )
            if not created:
                # if exists and not approved, update
                if bildirim.OnayDurumu == 1:
                    return JsonResponse({'status': 'error', 'message': 'Bildirim zaten onaylanmış, güncellenemez.'}, status=400)
                bildirim.MesaiDetay = mesai_detay
                bildirim.IcapDetay = icap_detay
                bildirim.NormalFazlaMesai = normal
                bildirim.BayramFazlaMesai = bayram
                bildirim.RiskliNormalFazlaMesai = rnormal
                bildirim.RiskliBayramFazlaMesai = rbayram
                bildirim.GeceNormalFazlaMesai = gnormal
                bildirim.GeceBayramFazlaMesai = gbayram
                bildirim.GeceRiskliNormalFazlaMesai = grnormal
                bildirim.GeceRiskliBayramFazlaMesai = grbayram
                bildirim.NormalIcap = nicap
                bildirim.BayramIcap = bicap
                bildirim.OlusturanKullanici = request.user
                bildirim.save()

        bildirim_data = {
            'personel_id': personel.PersonelID,
            'bildirim_id': bildirim.BildirimID,
            'normal_mesai': float(bildirim.NormalFazlaMesai),
            'bayram_mesai': float(bildirim.BayramFazlaMesai),
            'riskli_normal': float(bildirim.RiskliNormalFazlaMesai),
            'riskli_bayram': float(bildirim.RiskliBayramFazlaMesai),
            'gece_normal_mesai': float(bildirim.GeceNormalFazlaMesai),
            'gece_bayram_mesai': float(bildirim.GeceBayramFazlaMesai),
            'gece_riskli_normal': float(bildirim.GeceRiskliNormalFazlaMesai),
            'gece_riskli_bayram': float(bildirim.GeceRiskliBayramFazlaMesai),
            'toplam_mesai': float(bildirim.NormalFazlaMesai + bildirim.BayramFazlaMesai + bildirim.RiskliNormalFazlaMesai + bildirim.RiskliBayramFazlaMesai + bildirim.GeceNormalFazlaMesai + bildirim.GeceBayramFazlaMesai + bildirim.GeceRiskliNormalFazlaMesai + bildirim.GeceRiskliBayramFazlaMesai),
            'normal_icap': float(bildirim.NormalIcap),
            'bayram_icap': float(bildirim.BayramIcap),
            'toplam_icap': float(bildirim.ToplamIcap),
            'MesaiDetay': bildirim.MesaiDetay or {},
            'IcapDetay': bildirim.IcapDetay or {},
            'onay_durumu': int(bildirim.OnayDurumu or 0),
            'mutemet_kilit': bool(bildirim.MutemetKilit),
        }

        return JsonResponse({'status': 'success', 'bildirim_data': bildirim_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def bildirim_toplu_olustur(request, birim_id):
    if not request.user.has_permission('ÇS 657 Bildirim İşlemleri'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    try:
        data = json.loads(request.body)
        year = int(data.get('year'))
        month = int(data.get('month'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz parametre.'}, status=400)

    birim = Birim.objects.filter(BirimID=birim_id).first()
    if not birim:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
    if not liste:
        return JsonResponse({'status': 'error', 'message': 'Personel listesi yok.'}, status=404)

    donem_baslangic = date(year, month, 1)
    count = 0
    for kayit in liste.kayitlar.select_related('personel'):
        personel = kayit.personel
        # reuse bildirim_olustur logic by constructing a fake request body
        fake_body = json.dumps({'personel_id': personel.PersonelID, 'birim_id': birim.BirimID, 'donem': f'{year}/{month:02d}'})
        subreq = request
        subreq._body = fake_body.encode('utf-8')
        # call internal function
        resp = bildirim_olustur(subreq)
        try:
            rdata = json.loads(resp.content)
            if rdata.get('status') == 'success':
                count += 1
        except Exception:
            continue

    return JsonResponse({'status': 'success', 'message': f'{count} bildirim oluşturuldu/güncellendi.', 'count': count})


@login_required
@require_POST
def bildirim_tekil_onay(request, bildirim_id):
    if not request.user.has_permission('ÇS 657 Bildirim Onaylama'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    try:
        data = json.loads(request.body)
        onay = int(data.get('onay_durumu'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz parametre.'}, status=400)

    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if bildirim.MutemetKilit:
        return JsonResponse({'status': 'error', 'message': 'Bu bildirim kilitli.'}, status=400)

    if onay == 1:
        bildirim.OnayDurumu = 1
        bildirim.OnaylayanKullanici = request.user
        bildirim.OnayTarihi = timezone.now()
        bildirim.save()
        message = 'Bildirim onaylandı.'
    else:
        bildirim.OnayDurumu = 0
        bildirim.OnaylayanKullanici = None
        bildirim.OnayTarihi = None
        bildirim.save()
        message = 'Bildirim onayı kaldırıldı.'

    bildirim_data = {
        'personel_id': bildirim.Personel.PersonelID,
        'bildirim_id': bildirim.BildirimID,
        'normal_mesai': float(bildirim.NormalFazlaMesai),
        'bayram_mesai': float(bildirim.BayramFazlaMesai),
        'riskli_normal': float(bildirim.RiskliNormalFazlaMesai),
        'riskli_bayram': float(bildirim.RiskliBayramFazlaMesai),
        'toplam_mesai': float(bildirim.ToplamFazlaMesai),
        'normal_icap': float(bildirim.NormalIcap),
        'bayram_icap': float(bildirim.BayramIcap),
        'toplam_icap': float(bildirim.ToplamIcap),
        'MesaiDetay': bildirim.MesaiDetay or {},
        'IcapDetay': bildirim.IcapDetay or {},
        'onay_durumu': int(bildirim.OnayDurumu or 0),
        'mutemet_kilit': bool(bildirim.MutemetKilit),
    }

    return JsonResponse({'status': 'success', 'message': message, 'bildirim_data': bildirim_data})


@login_required
@require_POST
def bildirim_toplu_onay(request, birim_id):
    if not request.user.has_permission('ÇS 657 Bildirim Onaylama'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    try:
        data = json.loads(request.body)
        year = int(data.get('year'))
        month = int(data.get('month'))
        onay = int(data.get('onay_durumu'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz parametre.'}, status=400)

    birim = Birim.objects.filter(BirimID=birim_id).first()
    if not birim:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
    if not liste:
        return JsonResponse({'status': 'error', 'message': 'Personel listesi yok.'}, status=404)

    donem_baslangic = date(year, month, 1)
    qs = Bildirim.objects.filter(PersonelListesi=liste, DonemBaslangic=donem_baslangic, SilindiMi=False, MutemetKilit=False)
    count = 0
    for b in qs:
        if onay == 1:
            b.OnayDurumu = 1
            b.OnaylayanKullanici = request.user
            b.OnayTarihi = timezone.now()
        else:
            b.OnayDurumu = 0
            b.OnaylayanKullanici = None
            b.OnayTarihi = None
        b.save()
        count += 1

    return JsonResponse({'status': 'success', 'message': f'{count} bildirim güncellendi.', 'count': count})

@login_required
def bildirim_form(request, birim_id):
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
        messages.error(request, "Yetkiniz yok.")
        return HttpResponseForbidden("Yetkiniz yok.")

    # year & month from query params (expected ?year=YYYY&month=M)
    try:
        year = int(request.GET.get('year') or datetime.now().year)
        month = int(request.GET.get('month') or datetime.now().month)
    except Exception:
        year = datetime.now().year
        month = datetime.now().month

    # header/context similar to cizelge_yazdir
    kurum = "Kayseri Devlet Hastanesi"
    dokuman_kodu = "KU.FR.07"
    ay_ismi = get_turkish_month_name(month)
    form_adi = f"{year} Yılı {ay_ismi} Fazla Mesai Bildirim Formu"

    # resolve birim
    birim = Birim.objects.filter(BirimID=birim_id).first() or Birim.objects.filter(id=birim_id).first()
    if not birim:
        return HttpResponse(f"Birim bulunamadı: {birim_id}", status=404)

    # find personel list
    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()

    # Birim adı
    birim_adi = birim.BirimAdi if hasattr(birim, 'BirimAdi') else getattr(birim, 'name', 'Birim Adı Yok')

    # prepare days and resmi tatil info similar to cizelge_yazdir
    num_days = calendar.monthrange(year, month)[1]
    tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
    resmi_tatil_gunleri = [t.TatilTarihi for t in tatiller]

    days = []
    for day_num in range(1, num_days + 1):
        current_date = date(year, month, day_num)
        is_weekend = current_date.weekday() >= 5
        is_holiday = current_date in resmi_tatil_gunleri
        days.append({
            'day_num': day_num,
            'full_date': current_date.strftime('%Y-%m-%d'),
            'is_weekend': is_weekend,
            'is_holiday': is_holiday,
        })

    personel_rows = []
    if liste:
        kayitlar = liste.kayitlar.select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname')
        for kayit in kayitlar:
            p = kayit.personel
            # get bildirim if exists
            donem_baslangic = date(year, month, 1)
            bildirim = Bildirim.objects.filter(Personel=p, DonemBaslangic=donem_baslangic, SilindiMi=False).first()

            normal = bildirim.NormalFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            gece_normal = bildirim.GeceNormalFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            
            bayram = bildirim.BayramFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            gece_bayram = bildirim.GeceBayramFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            
            rnormal = bildirim.RiskliNormalFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            gece_rnormal = bildirim.GeceRiskliNormalFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            
            rbayram = bildirim.RiskliBayramFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            gece_rbayram = bildirim.GeceRiskliBayramFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')

            nicap = bildirim.NormalIcap or Decimal('0.0') if bildirim else Decimal('0.0')
            bicap = bildirim.BayramIcap or Decimal('0.0') if bildirim else Decimal('0.0')

            daily_mesai = bildirim.MesaiDetay if (bildirim and bildirim.MesaiDetay) else {}
            icap_daily = bildirim.IcapDetay if (bildirim and bildirim.IcapDetay) else {}
            onay = int(bildirim.OnayDurumu) if (bildirim and bildirim.OnayDurumu is not None) else 0

            personel_rows.append({
                'sira_no': kayit.sira_no or 0,
                'personel': p,
                'normal_fazla_mesai': normal,
                'gece_normal_fazla_mesai': gece_normal,
                'bayram_fazla_mesai': bayram,
                'gece_bayram_fazla_mesai': gece_bayram,
                'riskli_normal': rnormal,
                'gece_riskli_normal': gece_rnormal,
                'riskli_bayram': rbayram,
                'gece_riskli_bayram': gece_rbayram,
                'normal_icap': nicap,
                'bayram_icap': bicap,
                'toplam': (normal + gece_normal + bayram + gece_bayram + rnormal + gece_rnormal + rbayram + gece_rbayram),
                'daily_mesai': daily_mesai,
                'icap_daily': icap_daily,
                'onay_durumu': onay,
            })

    # Prepare PDF-specific context using the supplied PDF template (bildirim_formu.html)
    try:
        file_url = f"file:///{staticfiles_storage.path('logo/kdh_logo.png')}"
    except Exception:
        file_url = None

    # Prepare personeller list for the PDF template by mapping existing personel_rows
    resmi_tatil_gunleri_nums = []
    arefe_gunleri_nums = []
    try:
        tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
        resmi_tatil_gunleri_nums = [t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM']
        arefe_gunleri_nums = [t.TatilTarihi.day for t in tatiller if t.ArefeMi]
    except Exception:
        pass

    personellers = []
    for row in personel_rows:
        p = row.get('personel')
        daily = row.get('daily_mesai') or {}
        icap_daily = row.get('icap_daily') or {}
        onay_durumu = "Onaylandı" if row.get('onay_durumu', 0) == 1 else "Beklemede"
        mesai_data = []
        for d in days:
            key = d['full_date']
            entry = daily.get(key, {})
            icap_val = icap_daily.get(key, 0)
            
            if isinstance(entry, dict):
                saat = entry.get('saat', '')
                izinad = entry.get('izin', '')
                mesai_notu = entry.get('not', '')
            else:
                saat = entry or ''
                izinad = ''
                mesai_notu = ''
            md = {
                'MesaiTanimID': None,
                'Saat': saat,
                'IzinAd': izinad,
                'MesaiNotu': mesai_notu,
                'IcapSure': icap_val if icap_val > 0 else None,
                'is_weekend': d.get('is_weekend', False),
                'is_holiday': (d['day_num'] in resmi_tatil_gunleri_nums),
                'is_arife': (d['day_num'] in arefe_gunleri_nums),
            }
            mesai_data.append(md)

        personellers.append({
            'PersonelName': getattr(p, 'PersonelName', ''),
            'PersonelSurname': getattr(p, 'PersonelSurname', ''),
            'PersonelTCKN': getattr(p, 'PersonelTCKN', ''),
            'PersonelTitle': getattr(p, 'PersonelTitle', ''),
            'normal_fazla_mesai': row.get('normal_fazla_mesai'),
            'gece_normal_fazla_mesai': row.get('gece_normal_fazla_mesai'),
            'bayram_fazla_mesai': row.get('bayram_fazla_mesai'),
            'gece_bayram_fazla_mesai': row.get('gece_bayram_fazla_mesai'),
            'riskli_normal': row.get('riskli_normal'),
            'gece_riskli_normal': row.get('gece_riskli_normal'),
            'riskli_bayram': row.get('riskli_bayram'),
            'gece_riskli_bayram': row.get('gece_riskli_bayram'),
            'normal_icap': row.get('normal_icap'),
            'bayram_icap': row.get('bayram_icap'),
            'mesai_data': mesai_data,
            'hesaplama': {'fazla_mesai': None},
            'onay_durumu': onay_durumu,
        })

    # İlgili dönemdeki ek mesaileri topla
    ek_mesai_list = []
    if liste:
        for kayit in liste.kayitlar.select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname'):
            p = kayit.personel
            ems = EkMesai.objects.filter(
                mesai__Personel=p,
                mesai__MesaiDate__year=year,
                mesai__MesaiDate__month=month
            ).order_by('mesai__MesaiDate', 'Baslangic')
            
            if ems.exists():
                em_strings = []
                for em in ems:
                    sure_str = f"{int(em.Sure)}" if em.Sure % 1 == 0 else f"{em.Sure}".replace('.', ',')
                    em_strings.append(f"{em.mesai.MesaiDate.strftime('%d.%m.%Y')}({em.Baslangic.strftime('%H:%M')}-{em.Bitis.strftime('%H:%M')}-{sure_str} Saat)")
                ek_mesai_list.append(f"{p.PersonelName} {p.PersonelSurname}: {', '.join(em_strings)}")

    # prepare context matching the PDF template
    context_pdf = {
        'kurum': kurum,
        'dokuman_kodu': dokuman_kodu,
        'form_adi': form_adi,
        'yayin_tarihi': 'Haziran 2018',
        'revizyon_tarihi': 'Ekim 2025',
        'revizyon_no': '02',
        'sayfa_no': '1',
        'birim_adi': birim_adi,
        'pdf_logo': file_url,
        'personellers': personellers,
        'personeller': personellers,
        'days': days,
        'resmi_tatil_gunleri': resmi_tatil_gunleri_nums,
        'arefe_gunleri': arefe_gunleri_nums,
        'year': year,
        'month': month,
        'aciklama': liste.aciklama if liste else '',
        'ek_mesai_list': ek_mesai_list,
    }

    # Render PDF template and generate PDF (landscape)
    try:
        template = get_template('mercis657/pdf/bildirim_formu.html')
        html = template.render({**context_pdf})
    except Exception:
        html = render_to_string('mercis657/pdf/bildirim_formu.html', context_pdf)

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': '',
        'enable-external-links': True,
        'quiet': ''
    }

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"bildirim_form_{birim.BirimAdi}_{year}_{month:02d}.pdf"
    filename = filename.replace(' ', '_')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

@login_required
@require_POST
def bildirim_riskli_sure_guncelle(request):
    """
    Manuel girilen riskli mesai sürelerini kaydeder ve normal mesai sürelerini düşer.
    """
    if not request.user.has_permission('ÇS 657 Bildirim İşlemleri'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
        
    try:
        data = json.loads(request.body)
        guncellemeler = data.get('guncellemeler', [])
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz parametre.'}, status=400)

    count = 0
    with transaction.atomic():
        for item in guncellemeler:
            bildirim_id = item.get('bildirim_id')
            if not bildirim_id:
                continue
            
            bildirim = Bildirim.objects.filter(pk=bildirim_id, MutemetKilit=False, OnayDurumu=0).first()
            if not bildirim:
                continue

            # Parse inputs into Decimal
            rnormal = Decimal(str(item.get('riskli_normal', 0.0)))
            rbayram = Decimal(str(item.get('riskli_bayram', 0.0)))
            grnormal = Decimal(str(item.get('gece_riskli_normal', 0.0)))
            grbayram = Decimal(str(item.get('gece_riskli_bayram', 0.0)))
            
            # 1. Havuz mantığı: orijinal toplamı bul (Normal + Daha önce riskli yapılan)
            original_normal = bildirim.NormalFazlaMesai + bildirim.RiskliNormalFazlaMesai
            original_bayram = bildirim.BayramFazlaMesai + bildirim.RiskliBayramFazlaMesai
            original_gnormal = bildirim.GeceNormalFazlaMesai + bildirim.GeceRiskliNormalFazlaMesai
            original_gbayram = bildirim.GeceBayramFazlaMesai + bildirim.GeceRiskliBayramFazlaMesai

            # 2. Girilen sayı orijinali aşamaz, aşarsa cap'le
            if rnormal > original_normal: rnormal = original_normal
            if rbayram > original_bayram: rbayram = original_bayram
            if grnormal > original_gnormal: grnormal = original_gnormal
            if grbayram > original_gbayram: grbayram = original_gbayram

            # 3. Yeni değerleri tanımla ve normal sureleri azalt (original - riskli_yeni)
            bildirim.RiskliNormalFazlaMesai = rnormal
            bildirim.NormalFazlaMesai = original_normal - rnormal

            bildirim.RiskliBayramFazlaMesai = rbayram
            bildirim.BayramFazlaMesai = original_bayram - rbayram

            bildirim.GeceRiskliNormalFazlaMesai = grnormal
            bildirim.GeceNormalFazlaMesai = original_gnormal - grnormal

            bildirim.GeceRiskliBayramFazlaMesai = grbayram
            bildirim.GeceBayramFazlaMesai = original_gbayram - grbayram

            bildirim.save()
            count += 1

    return JsonResponse({'status': 'success', 'message': f'{count} bildirim başarıyla güncellendi.', 'count': count})

```

---

### Dosya: views\birim_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\birim_views.py`

```python
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Birim, UserBirim, Kurum, UstBirim, Idareci
import json
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

def birim_yonetim(request):
    birimler = Birim.objects.select_related('Kurum', 'UstBirim', 'Idareci').all()
    birim_list = []
    for birim in birimler:
        yetkiler = UserBirim.objects.filter(birim=birim).select_related('user')
        yetkili_users = [
            {
                "username": y.user.Username,
                "full_name": y.user.FullName
            }
            for y in yetkiler
        ]
        birim_list.append({
            "id": birim.BirimID,
            "adi": birim.BirimAdi,
            "kurum": birim.Kurum.ad if birim.Kurum else "",
            "ust_birim": birim.UstBirim.ad if birim.UstBirim else "",
            "idareci": birim.Idareci.ad if birim.Idareci else "",
            "pasif": birim.Pasif,
            "yetkili_sayisi": len(yetkili_users),
            "yetkililer": yetkili_users,
        })
    kurumlar = Kurum.objects.all()
    ust_birimler = UstBirim.objects.all()
    idareciler = Idareci.objects.all()
    return render(request, "mercis657/birim_yonetim.html", {
        "birimler": birim_list,
        "kurumlar": kurumlar,
        "ust_birimler": ust_birimler,
        "idareciler": idareciler,
    })

@csrf_exempt
def birim_ekle(request):
    if request.method == 'POST':
        ad = request.POST.get('BirimAdi')
        kurum_id = request.POST.get('Kurum') or None
        ust_id = request.POST.get('UstBirim') or None
        mudur_id = request.POST.get('idareci') or None
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Birim adı zorunlu.'})
        try:
            birim = Birim.objects.create(
                BirimAdi=ad,
                Kurum_id=kurum_id if kurum_id else None,
                UstBirim_id=ust_id if ust_id else None,
                Idareci_id=mudur_id if mudur_id else None
            )
            # Yeni eklenen birime mevcut kullanıcıyı yetkilendir
            UserBirim.objects.create(user=request.user, birim=birim)
            return JsonResponse({'status': 'success', 'birim_id': birim.BirimID})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})

@login_required
def birim_detay(request, birim_id):
    try:
        birim = get_object_or_404(Birim, BirimID=birim_id)
        # Kullanıcının bu birim için yetkisi veya "ÇS 657 Tüm Birimleri Görebilir" yetkisi var mı kontrol et
        if not request.user.has_permission("ÇS 657 Tüm Birimleri Görebilir"):
            if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
                return JsonResponse({'status': 'error', 'message': 'Bu birim için yetkiniz yok.'}, status=403)

        data = {
            'BirimID': birim.BirimID,
            'BirimAdi': birim.BirimAdi,
            'Kurum': birim.Kurum.pk if birim.Kurum else None,
            'UstBirim': birim.UstBirim.pk if birim.UstBirim else None,
            'idareci': birim.Idareci.pk if birim.Idareci else None,
        }
        return JsonResponse({'status': 'success', 'data': data})
    except Birim.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt # CSRF korumasını geçici olarak devre dışı bırakıyoruz, uygun token yönetimi eklenmeli
@require_POST
@login_required
def birim_guncelle(request, birim_id):
    try:
        birim = get_object_or_404(Birim, BirimID=birim_id)
        # Kullanıcının bu birim için yetkisi veya "ÇS 657 Tüm Birimleri Görebilir" yetkisi var mı kontrol et
        if not request.user.has_permission("ÇS 657 Tüm Birimleri Görebilir"):
            if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
                return JsonResponse({'status': 'error', 'message': 'Bu birim için yetkiniz yok.'}, status=403)

        ad = request.POST.get('birimAdi')
        kurum_id = request.POST.get('Kurum') or None
        ust_id = request.POST.get('UstBirim') or None
        mudur_id = request.POST.get('idareci') or None

        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Birim adı zorunlu.'})

        birim.BirimAdi = ad
        birim.Kurum_id = kurum_id
        birim.UstBirim_id = ust_id
        birim.Idareci_id = mudur_id
        birim.save()

        return JsonResponse({'status': 'success', 'message': 'Birim başarıyla güncellendi.'})
    except Birim.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt # CSRF korumasını geçici olarak devre dışı bırakıyoruz, uygun token yönetimi eklenmeli
@require_POST
@login_required
def birim_sil(request, birim_id):
    try:
        birim = get_object_or_404(Birim, BirimID=birim_id)
        # Kullanıcının bu birim için yetkisi veya "ÇS 657 Tüm Birimleri Görebilir" yetkisi var mı kontrol et
        if not request.user.has_permission("ÇS 657 Tüm Birimleri Görebilir"):
            if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
                return JsonResponse({'status': 'error', 'message': 'Bu birim için yetkiniz yok.'}, status=403)

        birim.Pasif = True
        birim.save()
        return JsonResponse({'status': 'success', 'message': 'Birim başarıyla silindi.'})
    except Birim.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def birim_yetki_ekle(request, birim_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user = User.objects.get(Username=username)
            birim = Birim.objects.get(pk=birim_id)
            obj, created = UserBirim.objects.get_or_create(user=user, birim=birim)
            if created:
                messages.success(request, f"{user.FullName} kullanıcısına {birim.BirimAdi} birimi yetkisi verildi.")
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error", "message": "Kullanıcı zaten yetkili."})
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı."})
        except Birim.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Birim bulunamadı."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Geçersiz istek."})

@csrf_exempt
@require_POST
def birim_yetki_sil(request, birim_id):
    # Yetki kontrolü
    if not request.user.has_permission("ÇS 657 Birim Yönetimi Sayfası"):
        if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
            return JsonResponse({"status": "error", "message": "Bu birim için yetkiniz yok."}, status=403)
    
    try:
        body = json.loads(request.body)
        username = body.get('username')
        user = User.objects.get(Username=username)
        birim = Birim.objects.get(pk=birim_id)
        deleted, _ = UserBirim.objects.filter(user=user, birim=birim).delete()
        if deleted:
            messages.success(request, f"{user.FullName} kullanıcısının {birim.BirimAdi} birimi yetkisi kaldırıldı.")
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Yetki bulunamadı."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
    
def birim_yetkililer(request, birim_id):
    # Birime atanmış kullanıcıları getir
    yetkiler = UserBirim.objects.filter(birim_id=birim_id).select_related('user')
    data = [
        {
            "username": y.user.Username,
            "full_name": y.user.FullName,
        }
        for y in yetkiler
    ]
    return JsonResponse({"status": "success", "data": data})

def kullanici_ara(request):
    username = request.GET.get('username', '').strip()
    try:
        user = User.objects.get(Username=username)
        data = {
            "username": user.Username,
            "full_name": user.FullName
        }
        return JsonResponse({"status": "success", "data": data})
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı."})


@csrf_exempt
def kurum_ekle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Kurum adı zorunlu.'})
        if Kurum.objects.filter(ad=ad).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad ile kurum zaten var.'})
        Kurum.objects.create(ad=ad)
        messages.success(request, f'{ad} isimli Kurum başarıyla eklendi.')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def kurum_guncelle(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Kurum adı zorunlu.'})
        kurum = Kurum.objects.get(pk=pk)
        kurum.ad = ad
        kurum.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def kurum_sil(request, pk):
    if request.method == 'POST':
        try:
            kurum = Kurum.objects.get(pk=pk)
            kurum.delete()
            messages.success(request, f'{kurum.ad} isimli Kurum başarıyla silindi.')
            return JsonResponse({'status': 'success'})
        except Kurum.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Kurum bulunamadı.'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def ust_birim_ekle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Üst birim adı zorunlu.'})
        if UstBirim.objects.filter(ad=ad).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad ile üst birim zaten var.'})
        UstBirim.objects.create(ad=ad)
        messages.success(request, f'{ad} isimli Üst Birim başarıyla eklendi.')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def ust_birim_guncelle(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Üst birim adı zorunlu.'})
        ust = UstBirim.objects.get(pk=pk)
        ust.ad = ad
        ust.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def ust_birim_sil(request, pk):
    if request.method == 'POST':
        try:
            ust = UstBirim.objects.get(pk=pk)
            ust.delete()
            messages.success(request, f'{ust.ad} isimli Üst Birim başarıyla silindi.')
            return JsonResponse({'status': 'success'})
        except UstBirim.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Üst birim bulunamadı.'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def idareci_ekle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'İdareci adı zorunlu.'})
        if Idareci.objects.filter(ad=ad).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad ile idareci zaten var.'})
        Idareci.objects.create(ad=ad)
        messages.success(request, f'{ad} isimli İdareci başarıyla eklendi.')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def idareci_guncelle(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'İdareci adı zorunlu.'})
        idareci = Idareci.objects.get(pk=pk)
        idareci.ad = ad
        idareci.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def kurum_toggle_aktif(request, pk):
    if request.method == 'POST':
        try:
            kurum = Kurum.objects.get(pk=pk)
            kurum.aktif = not kurum.aktif
            kurum.save()
            messages.success(request, f"{kurum.ad} kurumunun durumu {'aktif' if kurum.aktif else 'pasif'} olarak güncellendi.")
            return JsonResponse({'status': 'success', 'aktif': kurum.aktif})
        except Kurum.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Kurum bulunamadı.'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def ust_birim_toggle_aktif(request, pk):
    if request.method == 'POST':
        try:
            ust = UstBirim.objects.get(pk=pk)
            ust.aktif = not ust.aktif
            ust.save()
            messages.success(request, f"{ust.ad} üst biriminin durumu {'aktif' if ust.aktif else 'pasif'} olarak güncellendi.")
            return JsonResponse({'status': 'success', 'aktif': ust.aktif})
        except UstBirim.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'İdare bulunamadı.'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def idareci_toggle_aktif(request, pk):
    if request.method == 'POST':
        try:
            idareci = Idareci.objects.get(pk=pk)
            idareci.aktif = not idareci.aktif
            idareci.save()
            messages.success(request, f"{idareci.ad} idarecisinin durumu {'aktif' if idareci.aktif else 'pasif'} olarak güncellendi.")
            return JsonResponse({'status': 'success', 'aktif': idareci.aktif})
        except Idareci.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'İdareci bulunamadı.'})
    return JsonResponse({'status': 'error'})

def kullanici_ara(request):
    username = request.GET.get('username', '').strip()
    try:
        user = User.objects.get(Username=username)
        data = {
            "username": user.Username,
            "full_name": user.FullName
        }
        return JsonResponse({"status": "success", "data": data})
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı."})
```

---

### Dosya: views\cizelge_edit_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\cizelge_edit_views.py`

```python
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime, date, timedelta
import calendar
import json
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.conf import settings
from pathlib import Path
from ..models import Mesai, Personel, PersonelListesi, PersonelListesiKayit, MesaiYedek, Mesai_Tanimlari, Izin, ResmiTatil, UstBirim, SabitMesai, EkMesai
from ..utils import hesapla_fazla_mesai, get_favori_mesailer, get_turkish_month_name, hesapla_fazla_mesai_sade
from PersonelYonSis.FMConnection.KDHIzin import IzinSorgula
import pdfkit
from django.conf import settings
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage

file_url = f"file:///{staticfiles_storage.path('logo/kdh_logo.png')}"

# PDFKit yapılandırması
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

@login_required
def cizelge_yazdir(request):
    # Çalışma listesi yazdırma sayfası

    # Parse query params: donem=YYYY/MM or year & month; birim_id
    donem = request.GET.get('donem') or request.GET.get('donem')
    birim_id = request.GET.get('birim_id') or request.GET.get('birim')

    # default header variables
    kurum = "Kayseri Devlet Hastanesi"
    dokuman_kodu = "KU.FR.07"

    # Build an absolute file:// path to the logo if STATIC_ROOT is set
    pdf_logo = file_url

    # Determine year/month
    year = None
    month = None
    if donem:
        try:
            parts = donem.split('/')
            if len(parts) >= 2:
                year = int(parts[0])
                month = int(parts[1])
        except Exception:
            year = None
            month = None
    # fallback to separate params
    if not year or not month:
        try:
            year = int(request.GET.get('year') or datetime.now().year)
            month = int(request.GET.get('month') or datetime.now().month)
        except Exception:
            year = datetime.now().year
            month = datetime.now().month

    # Prepare default empty context pieces
    days = []
    personeller_for_pdf = []
    resmi_tatil_gunleri = []
    arefe_gunleri = []

    try:
        import calendar
        # Resolve birim: Birim may use BirimID field
        from ..models import Birim as _Birim
        birim = None
        if birim_id:
            try:
                birim = _Birim.objects.filter(BirimID=birim_id).first() or _Birim.objects.filter(id=birim_id).first()
            except Exception:
                birim = None

        # Find the personel list for that birim and period
        liste = None
        if birim:
            liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()

        # Build days for month
        days_in_month = calendar.monthrange(year, month)[1]
        for d in range(1, days_in_month + 1):
            dow = calendar.weekday(year, month, d)  # 0 Mon .. 6 Sun
            is_weekend = dow >= 5
            days.append({'day_num': d, 'is_weekend': is_weekend})

        # Load resmi tatil list for month
        tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
        resmi_tatil_gunleri = [t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM']
        arefe_gunleri = [t.TatilTarihi.day for t in tatiller if t.ArefeMi]

        # If list exists, build person rows
        if liste:
            # iterate over kayitlar to preserve ordering
            for kayit in liste.kayitlar.select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname').all():
                p = kayit.personel
                # build mesai_data aligned with days
                mesai_data = []
                for d in days:
                    day_no = d['day_num']
                    from datetime import date
                    current_date = date(year, month, day_no)
                    mesai = Mesai.objects.filter(Personel=p, MesaiDate=current_date).select_related('MesaiTanim', 'Izin').first()
                    md = {
                        'MesaiTanimID': mesai.MesaiTanim_id if mesai else None,
                        'Saat': (mesai.MesaiTanim.Saat if (mesai and getattr(mesai, 'MesaiTanim', None)) else ''),
                        'IzinAd': (mesai.Izin.ad if (mesai and getattr(mesai, 'Izin', None)) else ''),
                        'MesaiNotu': getattr(mesai, 'MesaiNotu', '') if mesai else '',
                        'is_weekend': d['is_weekend'],
                        'is_holiday': (day_no in resmi_tatil_gunleri),
                        'is_arife': (day_no in arefe_gunleri),
                    }
                    mesai_data.append(md)
                
                #  Fazla mesai hesapla
                fazla_mesai_degeri = hesapla_fazla_mesai_sade(kayit, year, month)

                personeller_for_pdf.append({
                    'PersonelName': f"{ p.PersonelName} {p.PersonelSurname}",
                    'PersonelTitle': getattr(p, 'PersonelTitle', ''),
                    'mesai_data': mesai_data,
                    'hesaplama': {'fazla_mesai': fazla_mesai_degeri }
                })
    except Exception as e:
        # swallow and render template with whatever we have
        pass

    # Açıklama: GET parametresi öncelikli, yoksa PersonelListesi.aciklama
    aciklama_param = request.GET.get('aciklama', None)
    if aciklama_param is not None:
        aciklama = aciklama_param
    elif liste and hasattr(liste, 'aciklama'):
        aciklama = liste.aciklama or ""
    else:
        aciklama = ""

    ay_ismi = get_turkish_month_name(month)
    form_adi = f"{year} Yılı {ay_ismi} {birim.BirimAdi} Çalışma Listesi"

    # İlgili dönemdeki ek mesaileri topla
    ek_mesai_list = []
    if liste:
        for kayit in liste.kayitlar.select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname'):
            p = kayit.personel
            ems = EkMesai.objects.filter(
                mesai__Personel=p,
                mesai__MesaiDate__year=year,
                mesai__MesaiDate__month=month
            ).order_by('mesai__MesaiDate', 'Baslangic')
            
            if ems.exists():
                em_strings = []
                for em in ems:
                    sure_str = f"{int(em.Sure)}" if em.Sure % 1 == 0 else f"{em.Sure}".replace('.', ',')
                    em_strings.append(f"{em.mesai.MesaiDate.strftime('%d.%m.%Y')}({em.Baslangic.strftime('%H:%M')}-{em.Bitis.strftime('%H:%M')}-{sure_str} Saat)")
                ek_mesai_list.append(f"{p.PersonelName} {p.PersonelSurname}: {', '.join(em_strings)}")

    context = {
        'kurum': kurum,
        'dokuman_kodu': dokuman_kodu,
        'form_adi': form_adi,
        'yayin_tarihi': 'Haziran 2018',
        'revizyon_tarihi': 'Ekim 2025',
        'revizyon_no': '02',
        'sayfa_no': '1',
        'pdf_logo': pdf_logo,
        'personellers': personeller_for_pdf,
        'personeller': personeller_for_pdf,  # template expects 'personeller'
        'days': days,
        'resmi_tatil_gunleri': resmi_tatil_gunleri,
        'arefe_gunleri': arefe_gunleri,
        'year': year,
        'month': month,
        'liste': liste if 'liste' in locals() else None,
        'aciklama': aciklama,
        'ek_mesai_list': ek_mesai_list,
        'user': request.user,  # Giriş yapan kullanıcı bilgisi
    }

    # Pdf oluştur
    template = get_template('mercis657/pdf/calisma_listesi.html')
    html = template.render({ **context })  # context sözlüğünü açarak gönder
    # PDF ayarları
    options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': '',
        'enable-external-links': True,
        'quiet': ''
    }

    # PDF oluştur
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    # HTTP response oluştur (open in new tab)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Cizelge_{year}_{month}.pdf"'
    return response

@login_required
def cizelge_kaydet(request):
    if request.method == 'POST':
        changes = json.loads(request.body)
        errors = []
        listeler_to_sync = set()

        for key, data in changes.items():
            personel_id, mesai_date = key.split('_')
            mesai_date = datetime.strptime(mesai_date, "%Y-%m-%d").date()
            mesai_tanim_id = data.get('mesaiId')
            izin_id = data.get('izinId')
            mesai_notu = data.get('mesaiNotu')  # yeni alan
            icap = data.get('icap', False)

            # Kayıtlı mı kontrol et
            kayit_obj = PersonelListesiKayit.objects.filter(
                personel_id=personel_id,
                liste__yil=mesai_date.year,
                liste__ay=mesai_date.month
            ).first()
            
            if not kayit_obj:
                errors.append(f"Personel {personel_id} o ay listede değil.")
                continue

            listeler_to_sync.add(kayit_obj.liste_id)

            # Mevcut mesai kaydını bul
            try:
                existing_mesai = Mesai.objects.get(
                    Personel_id=personel_id,
                    MesaiDate=mesai_date
                )

                mesai_changed = existing_mesai.MesaiTanim_id != mesai_tanim_id
                izin_changed = existing_mesai.Izin_id != izin_id
                not_changed = (getattr(existing_mesai, 'MesaiNotu', None) or None) != (mesai_notu or None)
                icap_changed = existing_mesai.Icap != icap

                if not (mesai_changed or izin_changed or not_changed or icap_changed):
                    continue

                # Eğer zaten bekleyen değişiklik varken, gelen değer yedekle aynı ise vazgeçilmiş say
                last_backup = existing_mesai.yedekler.order_by('-created_at').first()
                if existing_mesai.Degisiklik and last_backup and \
                   last_backup.MesaiTanim_id == mesai_tanim_id and last_backup.Izin_id == izin_id and \
                   (getattr(existing_mesai, 'MesaiNotu', None) or None) == (mesai_notu or None):
                    # Icap değişimi yedeklenmiyor (RFC'de belirtilmese de basitlik için). Ancak Icap değiştiyse ve geri alındıysa?
                    # Icap yedekleme modelinde yoksa, direkt update edilebilir mi?
                    # MesaiYedek modelini değiştirmedik. Eğer Icap onay gerektiriyorsa (muhtemelen evet), MesaiYedek'e Icap eklemeliyiz mi?
                    # RFC "Icap" alanını Mesai'ye ekledi. MesaiYedek'e eklenmedi.
                    # Bu durumda Icap değişimi "Degisiklik" flagini tetikler mi?
                    # Varsayım: Icap değişimi direkt kaydedilir veya onay mekanizması dışında tutulur.
                    # Ancak "İcap Girişi" switch ile yapılıyor, kullanıcı kaydediyor.
                    # Modeldeki OnayDurumu icap için de geçerli mi?
                    # MesaiYedek'te Icap yoksa, Icap değişikliği "yedek" ile yönetilemez.
                    # Çözüm: Icap değişikliğini direkt yansıtıp, onay sürecine sokmayalım veya MesaiYedek güncelleyelim.
                    # Kullanıcı onayı beklemeden Icap güncellensin mi?
                    # Kodda MesaiYedek güncellemesi yapamayız çünkü model değişmedi.
                    # O yüzden Icap'i direkt güncelleyeceğiz.
                    existing_mesai.MesaiTanim_id = mesai_tanim_id
                    existing_mesai.Izin_id = izin_id
                    existing_mesai.MesaiNotu = mesai_notu
                    existing_mesai.Icap = icap # Icap restore/update
                    existing_mesai.OnayDurumu = True
                    existing_mesai.Degisiklik = False
                    existing_mesai.SistemdekiIzin = False
                    existing_mesai.save()
                    last_backup.delete()
                    continue

                # Onaylı kayıtta değişiklik -> yedekle ve beklemeye al (Sadece mesai/izin değiştiyse)
                # Icap değişikliği "Onay" gerektiriyor mu?
                # Eğer sadece Icap değiştiyse, ve Mesai/Izin aynıysa -> Direkt kaydet (Yedek olmadığı için)
                if (mesai_changed or izin_changed) and existing_mesai.OnayDurumu:
                    MesaiYedek.objects.create(
                        mesai=existing_mesai,
                        MesaiTanim_id=existing_mesai.MesaiTanim_id,
                        Izin_id=existing_mesai.Izin_id,
                        created_by=request.user
                    )
                    existing_mesai.OnayDurumu = False
                    existing_mesai.Degisiklik = True
                
                # Icap değişimi veya OnayDurumu zaten False ise veya yeni kayıt
                existing_mesai.MesaiTanim_id = mesai_tanim_id
                existing_mesai.Izin_id = izin_id
                existing_mesai.MesaiNotu = mesai_notu
                existing_mesai.Icap = icap
                existing_mesai.SistemdekiIzin = False  # manuel değişiklik
                
                # Manuel değişiklik yapıldığında riskli çalışma bilgisini sıfırla
                existing_mesai.riskli_calisma = None
                
                # Sadece Icap değiştiyse ve Mesai/Izin değişmediyse onay durumu bozulmasın (Yedek yok çünkü)
                if icap_changed and not (mesai_changed or izin_changed):
                     # OnayDurumu'nu ellemiyoruz (veya True yapıyoruz?)
                     pass 
                
                existing_mesai.save()

            except Mesai.DoesNotExist:
                # Yeni kayıt: onaylı ve değişiklik yok
                Mesai.objects.create(
                    Personel_id=personel_id,
                    MesaiDate=mesai_date,
                    MesaiTanim_id=mesai_tanim_id,
                    Izin_id=izin_id,
                    MesaiNotu=mesai_notu,
                    Icap=icap,
                    OnayDurumu=True,
                    Degisiklik=False
                )

        if errors:
            return JsonResponse({'status': 'partial', 'errors': errors})
            
        sync_results = []
        if listeler_to_sync:
            from ..sync_kayseri_api import sync_kayseri_mesai
            for liste_id in listeler_to_sync:
                res = sync_kayseri_mesai(liste_id)
                if res and res.get('durum') != 'BOS':
                    sync_results.append({'liste_id': liste_id, 'result': res})

        return JsonResponse({'status': 'success', 'sync_results': sync_results})

    return JsonResponse({'status': 'failed'}, status=400)

@login_required
def cizelge_onay(request):
    from datetime import date
    today = date.today()
    default_year = today.year
    default_month = today.month
    year = int(request.GET.get('year', default_year) or default_year)
    month = int(request.GET.get('month', default_month) or default_month)
    ust_birim_id = request.GET.get('ust_birim')

    from ..models import PersonelListesi

    pending_qs = Mesai.objects.filter(OnayDurumu=False, Degisiklik=True)
    if year and month:
        pending_qs = pending_qs.filter(MesaiDate__year=year, MesaiDate__month=month)

    personel_listeleri = PersonelListesi.objects.all()
    if year and month:
        personel_listeleri = personel_listeleri.filter(yil=year, ay=month)
    if ust_birim_id:
        personel_listeleri = personel_listeleri.filter(birim__UstBirim_id=ust_birim_id)

    cards = []
    for liste in personel_listeleri.select_related('birim'):
        person_ids = list(liste.kayitlar.values_list('personel_id', flat=True))
        cnt = pending_qs.filter(Personel_id__in=person_ids).count()
        if cnt:
            cards.append({'birim': liste.birim, 'yil': liste.yil, 'ay': liste.ay, 'count': cnt})

    # Filtre seçenekleri: yıl (geçen, bu, gelecek), ay (1-12), üst birimler
    years = [year-1, year, year+1]
    months = [{'value': i, 'label': i} for i in range(1,13)]
    ust_birimler = UstBirim.objects.all()

    return render(request, 'mercis657/cizelge_onay.html', {
        'cards': cards,
        'year': year,
        'month': month,
        'ust_birim_id': int(ust_birim_id) if (ust_birim_id and ust_birim_id.isdigit()) else '',
        'years': years,
        'months': months,
        'ust_birimler': ust_birimler,
    })

@login_required
def mesai_onayla(request, mesai_id):
    if not request.user.has_permission('ÇS 657 Çizelge Onay'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    mesai = Mesai.objects.filter(pk=mesai_id).first()
    if not mesai:
        return JsonResponse({'status': 'error', 'message': 'Kayıt bulunamadı.'}, status=404)
    mesai.OnayDurumu = True
    mesai.Degisiklik = False
    mesai.save()
    mesai.yedekler.all().delete()
    return JsonResponse({'status': 'success'})

@login_required
def mesai_reddet(request, mesai_id):
    if not request.user.has_permission('ÇS 657 Çizelge Onay'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    mesai = Mesai.objects.filter(pk=mesai_id).first()
    if not mesai:
        return JsonResponse({'status': 'error', 'message': 'Kayıt bulunamadı.'}, status=404)
    backup = mesai.yedekler.order_by('-created_at').first()
    if not backup:
        return JsonResponse({'status': 'error', 'message': 'Yedek bulunamadı.'}, status=400)
    mesai.MesaiTanim = backup.MesaiTanim
    mesai.Izin = backup.Izin
    mesai.OnayDurumu = True
    mesai.Degisiklik = False
    mesai.save()
    mesai.yedekler.all().delete()
    return JsonResponse({'status': 'success'})

@login_required
def toplu_onay(request, birim_id, year, month):
    if not request.user.has_permission('ÇS 657 Çizelge Onay'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    year = int(year)
    month = int(month)
    from ..models import PersonelListesi
    try:
        liste = PersonelListesi.objects.get(birim_id=birim_id, yil=year, ay=month)
    except PersonelListesi.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Personel listesi yok.'}, status=404)
    person_ids = list(liste.kayitlar.values_list('personel_id', flat=True))
    qs = Mesai.objects.filter(Personel_id__in=person_ids, MesaiDate__year=year, MesaiDate__month=month, OnayDurumu=False, Degisiklik=True)
    count = qs.count()
    for m in qs:
        m.OnayDurumu = True
        m.Degisiklik = False
        m.save()
        m.yedekler.all().delete()
    return JsonResponse({'status': 'success', 'count': count})

@login_required
def toplu_islem(request, liste_id, year, month):
    """Toplu işlemler modalını döner"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    liste = get_object_or_404(PersonelListesi, pk=liste_id)
    personeller = Personel.objects.filter(
        personellistesikayit__liste=liste
    ).distinct()
    mesai_tanimlari = get_favori_mesailer(request.user)

    # resmi tatil ve arefe günleri
    tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year, TatilTarihi__month=month
    )
    resmi_tatil_gunleri = [
        t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM'
    ]
    arefe_gunleri = [
        t.TatilTarihi.day for t in tatiller if t.ArefeMi
    ]
    sabit_mesailer = SabitMesai.objects.all()

    context = {
        'liste': liste,
        'personeller': personeller,
        'mesai_tanimlari': mesai_tanimlari,
        'year': year,
        'month': month,
        'sabit_mesailer': sabit_mesailer,
        'resmi_tatil_gunleri': resmi_tatil_gunleri,
        'extra_payload': {'liste_id': liste.id},  # her zaman dictionary
        'arefe_gunleri': arefe_gunleri,
        'disabled_days': [],  # toplu atamada genelde boş bırakabilirsin
        'toplu_mesai_ata_url': reverse(
            'mercis657:toplu_mesai_ata',
            args=[liste.id, year, month]
        ),
    }
    return render(request, 'mercis657/toplu_islem_modal.html', context)

@login_required
@require_POST
def toplu_radyasyon_ata(request, liste_id):
    """Tüm personele radyasyon çalışanı durumu atar"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        radyasyon_calisani = data.get('radyasyon_calisani', False)
        
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        updated_count = PersonelListesiKayit.objects.filter(
            liste=liste
        ).update(radyasyon_calisani=radyasyon_calisani)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{updated_count} personelin radyasyon durumu güncellendi.',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def toplu_mesai_ata(request, liste_id, year, month):
    """Tüm personele toplu mesai atar (resmi tatiller hariç)"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    try:
        data = json.loads(request.body)
        mesai_tanim_id = data.get('mesai_tanim_id')
        gunler = data.get('gunler', [])

        # Null veya geçersiz gün numaralarını ayıkla
        gunler = [int(g) for g in gunler if isinstance(g, int) and 1 <= g <= 31]

        if not mesai_tanim_id or not gunler:
            return JsonResponse({'status': 'error', 'message': 'Mesai tanımı ve günler seçilmelidir.'})

        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        mesai_tanim = get_object_or_404(Mesai_Tanimlari, pk=mesai_tanim_id)

        days_in_month = calendar.monthrange(year, month)[1]
        created_count = 0

        for personel in liste.kayitlar.all():
            for gun_no in gunler:
                # Ayın gün sınırını kontrol et
                if gun_no > days_in_month:
                    continue

                current_date = date(year, month, gun_no)

                # 📌 Resmi tatil kontrolü
                if ResmiTatil.objects.filter(TatilTarihi=current_date).exists():
                    continue  # resmi tatilde mesai yazma

                # Bu güne zaten mesai var mı kontrol et
                existing = Mesai.objects.filter(
                    Personel=personel.personel,
                    MesaiDate=current_date
                ).exists()

                if not existing:
                    Mesai.objects.create(
                        Personel=personel.personel,
                        MesaiDate=current_date,
                        MesaiTanim=mesai_tanim,
                        OnayDurumu=True,
                        Degisiklik=False
                    )
                    created_count += 1

        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} mesai kaydı oluşturuldu.',
            'created_count': created_count
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def get_or_create_izin_turu(izin_adi):
    izin_obj, created = Izin.objects.get_or_create(fm_karsiligi=izin_adi)
    return izin_obj

@login_required
@require_POST
def izinleri_mesailere_isle(request, liste_id):
    """
    liste_id ile ilişikli mesai kayıtları için izin kaydının olup olmadığını kontrol eder, varsa işler (FM'den çekerek).
    """
    try:
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        yil = liste.yil
        ay = liste.ay
        baslangic = date(yil, ay, 1)
        gun_sayisi = calendar.monthrange(yil, ay)[1]
        bitis = date(yil, ay, gun_sayisi)
        # baslangic ve bitis'i "YYYY-MM-DD" formatına çevirerek gönder
        izinler = IzinSorgula(
            baslangic=baslangic.strftime("%Y-%m-%d"),
            bitis=bitis.strftime("%Y-%m-%d")
        )
        updated_count = 0

        for row in izinler:
            tckn, baslangic_tarihi, bitis_tarihi, izin_turu = row
            izin_obj = get_or_create_izin_turu(izin_turu)
            personel = None
            # Personel listede mevcut mu kontrol et, varsa bu personeli kullan
            personel_listesi_kayit = liste.kayitlar.filter(personel__PersonelTCKN=tckn).first()
            if personel_listesi_kayit:
                personel = personel_listesi_kayit.personel
            else:
                continue  # Personel listede mevcut değilse atla

            start_date = datetime.strptime(str(baslangic_tarihi), "%Y-%m-%d").date()
            end_date = datetime.strptime(str(bitis_tarihi), "%Y-%m-%d").date() - timedelta(days=1)

            # Tarih aralığındaki mesaileri bul
            mesailer = Mesai.objects.filter(
                Personel=personel,
                MesaiDate__range=(start_date, end_date)
            )

            for mesai in mesailer:
                if mesai.Izin != izin_obj:
                    mesai.Izin = izin_obj
                    mesai.SistemdekiIzin = True  # sistemden gelen izin
                    mesai.MesaiTanim = None  # izinli günlerde mesai olmaz
                    mesai.save(update_fields=["Izin", "MesaiTanim", "SistemdekiIzin"])
                    updated_count += 1
                elif mesai.Izin == izin_obj:
                    mesai.SistemdekiIzin = True
                    mesai.save(update_fields=["SistemdekiIzin"])
                    updated_count += 1

        return JsonResponse({
            "status": "success",
            "message": f"{updated_count} mesai kaydı güncellendi.",
            "updated_count": updated_count
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
@require_POST
def toplu_mesai_degistir(request, liste_id, year, month):
    """Belirli bir mesaiyi başka bir mesai ile toplu olarak değiştirir"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    try:
        data = json.loads(request.body)
        eski_mesai_id = data.get('eski_mesai_id')
        yeni_mesai_id = data.get('yeni_mesai_id')
        
        # Eski ve yeni mesai ID'leri zorunlu
        if not eski_mesai_id or not yeni_mesai_id:
            return JsonResponse({'status': 'error', 'message': 'Eski ve yeni mesai seçimi zorunludur.'})
            
        eski_mesai_id = int(eski_mesai_id)
        yeni_mesai_id = int(yeni_mesai_id)

        # Liste ve tanımları al
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        
        # Yeni mesai tanımını kontrol et
        yeni_mesai = get_object_or_404(Mesai_Tanimlari, pk=yeni_mesai_id)
        
        person_ids = liste.kayitlar.values_list('personel_id', flat=True)
        
        mesailer = Mesai.objects.filter(
            Personel_id__in=person_ids,
            MesaiDate__year=year,
            MesaiDate__month=month,
            MesaiTanim_id=eski_mesai_id,
            SistemdekiIzin=False
        )
        
        updated_count = mesailer.update(
            MesaiTanim=yeni_mesai,
            OnayDurumu=True,
            Degisiklik=False
        )
        
        return JsonResponse({
            'status': 'success', 
            'message': f'{updated_count} adet mesai kaydı güncellendi.',
            'updated_count': updated_count
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def kayseri_sync_retry_view(request, liste_id):
    """
    Kullanıcının Kayseri API senkronizasyonunu manuel olarak yeniden denemesi için endpoint.
    """
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
        
    try:
        from ..sync_kayseri_api import sync_kayseri_mesai
        res = sync_kayseri_mesai(liste_id)
        return JsonResponse({'status': 'success', 'result': res})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

```

---

### Dosya: views\cizelge_kontrol_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\cizelge_kontrol_views.py`

```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from ..models import PersonelListesi, Mesai, Mesai_Tanimlari, Izin, SabitMesai, PersonelListesiKayit


@login_required
def cizelge_kontrol(request):
    """
    Çizelge hata kontrolü endpoint'i.
    
    Parameters:
        request.POST.liste_id (int): PersonelListesi ID
        request.POST.year (int): Yıl
        request.POST.month (int): Ay
    
    Returns:
        JsonResponse: 
        {
            "status": "success|error",
            "errors": [
                {
                    "type": str,
                    "message": str,
                    "personel_id": int,
                    "date": str,
                    "cell_selector": str
                }
            ]
        }
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        
        liste_id = int(data.get("liste_id"))
        year = int(data.get("year"))
        month = int(data.get("month"))

        if not all([liste_id, year, month]):
            raise ValidationError("Liste ID, yıl ve ay gerekli.")

        liste = PersonelListesi.objects.filter(pk=liste_id).first()
        if not liste:
            return JsonResponse({
                "status": "error",
                "message": "Personel listesi bulunamadı."
            }, status=404)

        errors = []
        
        # 24 saatlik mesai sonrası kontrolü
        errors.extend(_check_24_hour_mesai_rule(liste, year, month))
        
        # 5 gün boş bırakılmamalı kontrolü
        errors.extend(_check_5_day_empty_rule(liste, year, month))

        # Sabit mesai kontrolü ve güncellemesi
        errors.extend(sabit_mesai_kontrol(liste, year, month))

        return JsonResponse({
            "status": "success",
            "errors": errors
        })
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Hata: {str(e)}"
        }, status=500)


def _check_24_hour_mesai_rule(liste, year, month):
    """24 saatlik mesai sonrası kontrolü"""
    errors = []
    days_in_month = 31  # Max gün sayısı
    try:
        import calendar
        days_in_month = calendar.monthrange(year, month)[1]
    except:
        pass
    
    kayitlar = liste.kayitlar.select_related('personel').all()
    
    for kayit in kayitlar:
        if not getattr(kayit, 'is_gunduz_personeli', True):
            continue
        personel = kayit.personel
        mesailer = Mesai.objects.filter(
            Personel=personel,
            MesaiDate__year=year,
            MesaiDate__month=month
        ).select_related('MesaiTanim')
        
        for mesai in mesailer:
            if mesai.MesaiTanim and mesai.MesaiTanim.SonrakiGuneSarkiyor:
                if mesai.MesaiTanim.Sure and mesai.MesaiTanim.Sure >= 24:
                    # Sonraki günü kontrol et
                    next_date = mesai.MesaiDate + timedelta(days=1)
                    
                    # Sonraki gün aynı ay içindeyse kontrol et
                    if next_date.year == year and next_date.month == month:
                        next_mesai = Mesai.objects.filter(
                            Personel=personel,
                            MesaiDate=next_date
                        ).first()
                        
                        if next_mesai and next_mesai.MesaiTanim and not next_mesai.Izin:
                            errors.append({
                                "type": "24_hour_mesai",
                                "message": f"{mesai.MesaiDate.strftime('%Y-%m-%d')} tarihli 24 saatlik mesai sonrası {next_date.strftime('%Y-%m-%d')} tarihinde mesai tanımlanmamalı",
                                "personel_id": personel.PersonelID,
                                "date": next_date.strftime('%Y-%m-%d'),
                                "cell_selector": f"td[data-date='{next_date.strftime('%Y-%m-%d')}'][data-personel-id='{personel.PersonelID}']"
                            })
    
    return errors


def _check_5_day_empty_rule(liste, year, month):
    """5 gün boş bırakılmamalı kontrolü"""
    errors = []
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    
    kayitlar = liste.kayitlar.select_related('personel').all()
    
    for kayit in kayitlar:
        personel = kayit.personel
        
        # Önceki ayın son 4 gününü de kontrol et
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year = year - 1
        
        prev_days_in_month = calendar.monthrange(prev_year, prev_month)[1]
        start_check_date = date(prev_year, prev_month, max(1, prev_days_in_month - 3))
        end_check_date = date(year, month, days_in_month)
        
        # Tüm günleri kontrol et
        current_date = start_check_date
        consecutive_empty = 0
        empty_start = None
        
        while current_date <= end_check_date:
            # Hafta sonu ve resmi tatil kontrolü (basitleştirilmiş)
            weekday = current_date.weekday()
            is_weekend = weekday >= 5
            
            if not is_weekend:
                mesai = Mesai.objects.filter(
                    Personel=personel,
                    MesaiDate=current_date
                ).first()
                
                has_data = mesai and (mesai.MesaiTanim or mesai.Izin)
                
                if not has_data:
                    if consecutive_empty == 0:
                        empty_start = current_date
                    consecutive_empty += 1
                else:
                    if consecutive_empty >= 5:
                        errors.append({
                            "type": "5_day_empty",
                            "message": f"{personel.PersonelName} {personel.PersonelSurname} için {empty_start.strftime('%Y-%m-%d')} - {current_date.strftime('%Y-%m-%d')} arası {consecutive_empty} gün boyunca mesai verisi yok",
                            "personel_id": personel.PersonelID,
                            "date": empty_start.strftime('%Y-%m-%d'),
                            "cell_selector": f"td[data-date='{empty_start.strftime('%Y-%m-%d')}'][data-personel-id='{personel.PersonelID}']"
                        })
                    consecutive_empty = 0
                    empty_start = None
            
            current_date += timedelta(days=1)
        
        # Son kontrol: Eğer ay sonunda hala boş günler varsa
        if consecutive_empty >= 5:
            errors.append({
                "type": "5_day_empty",
                "message": f"{personel.PersonelName} {personel.PersonelSurname} için {empty_start.strftime('%Y-%m-%d')} - {end_check_date.strftime('%Y-%m-%d')} arası {consecutive_empty} gün boyunca mesai verisi yok",
                "personel_id": personel.PersonelID,
                "date": empty_start.strftime('%Y-%m-%d'),
                "cell_selector": f"td[data-date='{empty_start.strftime('%Y-%m-%d')}'][data-personel-id='{personel.PersonelID}']"
            })
    
    return errors


def sabit_mesai_kontrol(liste, year, month):
    """
    Personelin mesai saatlerine göre sabit mesai bilgisini günceller.
    """
    messages = []
    
    # Tüm sabit mesai tanımlarını al
    sabit_mesailer = SabitMesai.objects.all()
    sabit_mesai_map = {sm.aralik: sm for sm in sabit_mesailer}
    
    if not sabit_mesai_map:
        return messages
        
    kayitlar = liste.kayitlar.select_related('personel', 'sabit_mesai').all()
    
    for kayit in kayitlar:
        if not getattr(kayit, 'is_gunduz_personeli', True):
            continue
        personel = kayit.personel
        
        # Personelin ilgili dönemdeki mesailerini kontrol et
        mesailer = Mesai.objects.filter(
            Personel=personel,
            MesaiDate__year=year,
            MesaiDate__month=month
        ).select_related('MesaiTanim')
        
        sabit_mesai_counts = {}
        
        # Mesailer içinde sabit mesai aralığı ile eşleşenleri say
        for mesai in mesailer:
            if mesai.MesaiTanim and mesai.MesaiTanim.Saat in sabit_mesai_map:
                saat = mesai.MesaiTanim.Saat
                sabit_mesai_counts[saat] = sabit_mesai_counts.get(saat, 0) + 1
                
        matched_sabit_mesai = None
        if sabit_mesai_counts:
            # En çok eşleşen saati bul
            most_common_saat = max(sabit_mesai_counts, key=sabit_mesai_counts.get)
            matched_sabit_mesai = sabit_mesai_map[most_common_saat]
        
        # Eşleşme varsa ve mevcut kayıttan farklıysa güncelle
        if matched_sabit_mesai:
            if kayit.sabit_mesai != matched_sabit_mesai:
                kayit.sabit_mesai = matched_sabit_mesai
                kayit.save()
                
                messages.append({
                    "type": "info",
                    "message": f"{personel.PersonelName} {personel.PersonelSurname} isimli personelin sabit mesai kaydı {matched_sabit_mesai.aralik} olarak belirlendi",
                    "personel_id": personel.PersonelID,
                    "date": "",
                    "cell_selector": ""
                })
    
    return messages

```

---

### Dosya: views\ek_mesai_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\ek_mesai_views.py`

```python
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from ..models import EkMesai, Mesai
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
import datetime
from datetime import timedelta

@login_required
def ek_mesai_ekle(request, mesai_id):
    if not request.user.has_permission('ÇS 657 Stop Kaydı Ekleme'):
        messages.error(request, "Ek Mesai Ekleme yetkiniz yok.")
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    mesai = get_object_or_404(Mesai, pk=mesai_id)
    
    if request.method == "GET":
        mesai = Mesai.objects.select_related('Personel', 'MesaiTanim').prefetch_related('mercis657_ek_mesailer').get(pk=mesai_id)
        return render(request, "mercis657/ek_mesai_modal.html", {"mesai": mesai})

    if request.method == "POST":
        baslangic_raw = request.POST.get("Baslangic")
        bitis_raw = request.POST.get("Bitis")
        aciklama = request.POST.get("Aciklama")
        riskli = request.POST.get("Riskli") == 'on'
        
        if not baslangic_raw or not bitis_raw:
            return JsonResponse({'status': 'error', 'message': 'Zaman verisi eksik.'}, status=400)

        try:
            bas_time = datetime.time.fromisoformat(baslangic_raw)
            bit_time = datetime.time.fromisoformat(bitis_raw)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Zaman formatı okunamadı.'}, status=400)

        mesai_date = mesai.MesaiDate
        bas_dt = datetime.datetime.combine(mesai_date, bas_time)
        bit_dt = datetime.datetime.combine(mesai_date, bit_time)

        if bit_dt <= bas_dt:
            bit_dt = bit_dt + timedelta(days=1)

        if timezone.is_naive(bas_dt):
            bas_dt = timezone.make_aware(bas_dt, timezone.get_current_timezone())
        if timezone.is_naive(bit_dt):
            bit_dt = timezone.make_aware(bit_dt, timezone.get_current_timezone())

        ek_mesai = EkMesai.objects.create(
            mesai=mesai,
            Baslangic=bas_dt,
            Bitis=bit_dt,
            Aciklama=aciklama,
            Riskli=riskli,
            created_by=request.user,
        )
        return JsonResponse({"status": "success", "sure": ek_mesai.Sure})

@login_required
@require_POST
def ek_mesai_sil(request, ek_mesai_id):
    if not request.user.has_permission('ÇS 657 Stop Kaydı Ekleme'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    ek_mesai = get_object_or_404(EkMesai, pk=ek_mesai_id)
    ek_mesai.delete()
    return JsonResponse({"status": "deleted"})

```

---

### Dosya: views\fazla_mesai_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\fazla_mesai_views.py`

```python
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from ..models import PersonelListesiKayit, PersonelListesi, Personel
from ..utils import hesapla_fazla_mesai, hesapla_fazla_mesai_sade, get_vardiya_tanimlari

@login_required
def fazla_mesai_hesapla(request):
    """
    Seçili liste ve dönem için fazla mesai hesaplamalarını yapar.
    
    Parameters:
        request.GET.year (int): Yıl
        request.GET.month (int): Ay
        request.GET.liste_id (int): PersonelListesi ID
    
    Returns:
        JsonResponse: 
        {
            "status": "success|error",
            "data": [{"personel_id": id, "fazla_mesai": float}, ...],
            "message": "error message if any"
        }
    """
    try:
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        liste_id = int(request.GET.get("liste_id"))

        if not all([year, month, liste_id]):
            raise ValidationError("Yıl, ay ve liste ID gerekli.")

        # Resolve the PersonelListesi (safer) and iterate its kayitlar
        liste = PersonelListesi.objects.filter(pk=liste_id).first()
        if not liste:
            # No list found -> return empty success (matches other list endpoints)
            print(f"fazla_mesai_hesapla: PersonelListesi id={liste_id} bulunamadı")
            return JsonResponse({"status": "success", "data": []})

        kayitlar = liste.kayitlar.select_related('personel').all()

        sonuc = []
        for kayit in kayitlar:
            try:
                hesaplama = hesapla_fazla_mesai(kayit, year, month) or {}
                # hesapla_fazla_mesai returns keys 'normal_fazla_mesai' and 'bayram_fazla_mesai'
                normal = hesaplama.get('normal_fazla_mesai') or 0
                bayram = hesaplama.get('bayram_fazla_mesai') or 0
                # ensure Decimal -> float
                try:
                    normal_f = float(normal)
                except Exception:
                    normal_f = float(0)
                try:
                    bayram_f = float(bayram)
                except Exception:
                    bayram_f = float(0)

                toplam = normal_f + bayram_f
                sonuc.append({
                    "personel_id": kayit.personel.PersonelID,
                    "fazla_mesai": float(hesaplama.get('fazla_mesai')),
                    "normal_fazla_mesai": normal_f,
                    "bayram_fazla_mesai": bayram_f,
                })
            except Exception as e:
                print(f"fazla_mesai_hesapla: hata personel {getattr(kayit.personel, 'PersonelID', '?')}: {e}")
                continue

        return JsonResponse({
            "status": "success",
            "data": sonuc
        })
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Hesaplama hatası: {str(e)}"
        }, status=500)

@login_required
def fazla_mesai_hesapla_toplu(request):
    """
    Toplu fazla mesai hesaplama endpoint'i.
    
    Parameters:
        request.POST.personel_ids (list): Personel ID listesi
        request.POST.year (int): Yıl
        request.POST.month (int): Ay
        request.POST.liste_id (int): PersonelListesi ID
    
    Returns:
        JsonResponse: 
        {
            "status": "success|error",
            "data": [{"personel_id": id, "fazla_mesai": float}, ...],
            "message": "error message if any"
        }
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        
        personel_ids = data.get("personel_ids", [])
        year = int(data.get("year"))
        month = int(data.get("month"))
        liste_id = int(data.get("liste_id"))

        if not all([personel_ids, year, month, liste_id]):
            raise ValidationError("Personel ID listesi, yıl, ay ve liste ID gerekli.")

        liste = PersonelListesi.objects.filter(pk=liste_id).first()
        if not liste:
            return JsonResponse({
                "status": "error",
                "message": "Personel listesi bulunamadı."
            }, status=404)

        sonuc = []
        for personel_id in personel_ids:
            try:
                personel = Personel.objects.filter(PersonelID=int(personel_id)).first()
                if not personel:
                    continue
                
                kayit = PersonelListesiKayit.objects.filter(
                    liste=liste,
                    personel=personel
                ).first()
                
                if kayit:
                    fazla_mesai = hesapla_fazla_mesai_sade(kayit, year, month)
                    sonuc.append({
                        "personel_id": personel.PersonelID,
                        "fazla_mesai": float(fazla_mesai)
                    })
            except Exception as e:
                print(f"fazla_mesai_hesapla_toplu: hata personel {personel_id}: {e}")
                continue

        return JsonResponse({
            "status": "success",
            "data": sonuc
        })
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Hesaplama hatası: {str(e)}"
        }, status=500)


@login_required
def vardiya_tanimlari(request):
    """
    Vardiya tanımlarını döndürür.
    
    Returns:
        JsonResponse: 
        {
            "status": "success",
            "mesai_tanimlari": { id: { "gunduz": bool, "aksam": bool, "gece": bool } }
        }
    """
    try:
        tanimlar = get_vardiya_tanimlari()
        return JsonResponse({
            "status": "success",
            "mesai_tanimlari": tanimlar
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Hata: {str(e)}"
        }, status=500)
```

---

### Dosya: views\gunluk_izin_takibi_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\gunluk_izin_takibi_views.py`

```python
import os
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from ..models import Kurum, UstBirim, Idareci, Bina, Mesai, PersonelListesiKayit
import json
from datetime import datetime

@login_required
def gunluk_izin_takibi(request):
    """
    Günlük İzin Takibi sayfası.
    """
    sync_file_path = os.path.join(settings.BASE_DIR, 'mercis657', 'last_izin_sync.json')
    last_sync = None
    if os.path.exists(sync_file_path):
        try:
            with open(sync_file_path, 'r', encoding='utf-8') as f:
                last_sync = json.load(f)
        except Exception:
            pass

    context = {
        'kurumlar': Kurum.objects.filter(aktif=True),
        'ust_birimler': UstBirim.objects.filter(aktif=True),
        'idareciler': Idareci.objects.filter(aktif=True),
        'binalar': Bina.objects.filter(aktif=True),
        'bugun': datetime.now().strftime('%Y-%m-%d'),
        'last_sync': last_sync,
    }
    return render(request, 'mercis657/gunluk_izin_takibi.html', context)

@login_required
@require_POST
def gunluk_izin_takibi_search(request):
    """
    AJAX endpoint: Filtrelere göre İzinli Mesai kayıtlarını sorgular.
    JSON input: {kurum_id, ust_birim_id, idareci_id, bina_id, tarih}
    """
    try:
        data = json.loads(request.body)
        kurum_id = data.get('kurum_id')
        ust_birim_id = data.get('ust_birim_id')
        idareci_id = data.get('idareci_id')
        bina_id = data.get('bina_id')
        tarih = data.get('tarih')

        # İzinli olanları getir (Izin_id is not null)
        mesai_qs = Mesai.objects.filter(
            MesaiDate=tarih,
            Izin__isnull=False
        ).select_related(
            'Personel', 
            'Izin'
        )

        kayit_qs = PersonelListesiKayit.objects.filter(
            liste__yil=int(tarih.split('-')[0]),
            liste__ay=int(tarih.split('-')[1])
        ).select_related('liste__birim', 'personel')

        if kurum_id:
            kayit_qs = kayit_qs.filter(liste__birim__Kurum_id=kurum_id)
        if ust_birim_id:
            kayit_qs = kayit_qs.filter(liste__birim__UstBirim_id=ust_birim_id)
        if idareci_id:
            kayit_qs = kayit_qs.filter(liste__birim__Idareci_id=idareci_id)
        if bina_id:
            kayit_qs = kayit_qs.filter(liste__birim__Bina_id=bina_id)

        personel_ids = kayit_qs.values_list('personel_id', flat=True)
        mesai_qs = mesai_qs.filter(Personel_id__in=personel_ids)
        
        personel_birim_map = {}
        for kayit in kayit_qs:
            birim = kayit.liste.birim
            personel_birim_map[kayit.personel_id] = {
                'birim': birim.BirimAdi,
                'unvan': kayit.personel.PersonelTitle or ""
            }

        results = []
        for mesai in mesai_qs:
            p_info = personel_birim_map.get(mesai.Personel_id)
            if not p_info:
                continue 

            results.append({
                'birim': p_info['birim'],
                'personel_ad': f"{mesai.Personel.PersonelName} {mesai.Personel.PersonelSurname}",
                'unvan': p_info['unvan'],
                'sisteme_girildi': mesai.SistemdekiIzin,
                'izin_ad': mesai.Izin.ad if mesai.Izin else ""
            })

        # Sıralama: önce birim, sonra personel
        results.sort(key=lambda x: (x['birim'], x['personel_ad']))

        return JsonResponse({'status': 'success', 'results': results})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

```

---

### Dosya: views\ilk_liste_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\ilk_liste_views.py`

```python
# mercis657/views/ilk_liste_views.py
import calendar
from datetime import date
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import IlkListe, PersonelListesi, PersonelListesiKayit, Mesai, Personel, ResmiTatil
from ..utils import hesapla_fazla_mesai

@login_required
def ilk_liste_olustur(request, liste_id):
    try:
        liste = PersonelListesi.objects.get(pk=liste_id)
    except PersonelListesi.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Liste bulunamadı.'}, status=404)

    # Daha önce bu liste için oluşturulmuş ve onaylanmış bir ilk liste varsa engelle
    if IlkListe.objects.filter(PersonelListesi=liste, OnayDurumu=True).exists():
        return JsonResponse({'status': 'error', 'message': 'Bu liste için zaten ilk bildirim oluşturulmuş.'}, status=400)

    # Tüm personel kayıtlarını çek
    kayitlar = PersonelListesiKayit.objects.filter(liste=liste)
    veriler = []

    for kayit in kayitlar:
        mesailer = Mesai.objects.filter(
            Personel=kayit.personel,
            MesaiDate__year=liste.yil,
            MesaiDate__month=liste.ay
        )

        mesai_data = {}
        for m in mesailer:
            tarih = m.MesaiDate.strftime("%Y-%m-%d")
            if m.Izin:
                mesai_data[tarih] = {"izin": str(m.Izin)}
            elif m.MesaiTanim:
                mesai_data[tarih] = {"saat": str(m.MesaiTanim.Saat)}

        # Fazla mesai örneği (hesaplama fonksiyonundan alınabilir)
        fazla_mesai = hesapla_fazla_mesai(kayit, liste.yil, liste.ay)

        veriler.append({
            "personel": kayit.personel.PersonelID,
            "radyasyon_calisani": kayit.radyasyon_calisani,
            "mesai_data": mesai_data,
            "fazla_mesai": float(fazla_mesai.get('fazla_mesai') or 0),
        })

    ilk_liste = IlkListe.objects.create(
        PersonelListesi=liste,
        Veriler=veriler,
        OlusturanKullanici=request.user
    )

    return JsonResponse({
        'status': 'success',
        'message': 'İlk liste bildirimi oluşturuldu.',
        'ilk_liste_id': ilk_liste.id
    })

@login_required
def ilk_liste_detay(request, liste_id):
    ilk_liste = IlkListe.objects.filter(PersonelListesi_id=liste_id).order_by('-OlusturmaTarihi').first()
    if not ilk_liste:
        return JsonResponse({'status': 'error', 'message': 'Bu listeye ait ilk bildirim bulunamadı.'})

    yil = ilk_liste.PersonelListesi.yil
    ay = ilk_liste.PersonelListesi.ay

    # 🔹 Resmi tatil günleri
    resmi_tatiller = list(
        ResmiTatil.objects.filter(
            TatilTarihi__year=yil,
            TatilTarihi__month=ay
        ).values_list('TatilTarihi', flat=True)
    )
    resmi_tatiller_str = [t.strftime('%Y-%m-%d') for t in resmi_tatiller]

    # 🔹 Gün listesi
    days_in_month = calendar.monthrange(yil, ay)[1]
    days = [
        {
            'full_date': f"{yil}-{ay:02}-{gun:02}",
            'day_num': gun,
            'is_weekend': calendar.weekday(yil, ay, gun) >= 5,
            'is_resmi_tatil': f"{yil}-{ay:02}-{gun:02}" in resmi_tatiller_str
        }
        for gun in range(1, days_in_month + 1)
    ]

    veriler = []
    for v in ilk_liste.Veriler or []:
        try:
            p = Personel.objects.get(pk=v["personel"])
            v["personel_adi"] = f"{p.PersonelName} {p.PersonelSurname}"
        except Personel.DoesNotExist:
            v["personel_adi"] = f"ID {v['personel']} (Kayıt Yok)"
        veriler.append(v)

    onay_yetkisi = request.user.has_permission('ÇS 657 İlk Liste Bildirimi Onaylama')
    data = {
        "status": "success",
        "id": ilk_liste.id,
        "liste": f"{ilk_liste.PersonelListesi.birim} - {ilk_liste.PersonelListesi.yil}/{ilk_liste.PersonelListesi.ay}",
        "olusturan": ilk_liste.OlusturanKullanici.FullName if ilk_liste.OlusturanKullanici else "—",
        "olusturma_tarihi": ilk_liste.OlusturmaTarihi.strftime("%d.%m.%Y %H:%M"),
        "onay_durumu": ilk_liste.OnayDurumu,
        "veriler": veriler,
        "days": days,
        "onay_yetkisi": onay_yetkisi,
    }
    return JsonResponse(data)

@login_required
def ilk_liste_onayla(request, ilk_liste_id):
    try:
        ilk_liste = IlkListe.objects.get(pk=ilk_liste_id)
    except IlkListe.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'İlk liste bildirimi bulunamadı.'}, status=404)

    if not request.user.has_permission('ÇS 657 İlk Liste Bildirimi Onaylama'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    ilk_liste.onayla(request.user)
    return JsonResponse({'status': 'success', 'message': 'İlk liste bildirimi onaylandı.'})

@login_required
def ilk_liste_onay_kaldir(request, ilk_liste_id):
    try:
        ilk_liste = IlkListe.objects.get(pk=ilk_liste_id)
    except IlkListe.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'İlk liste bildirimi bulunamadı.'}, status=404)

    if not request.user.has_permission('ÇS 657 İlk Liste Bildirimi Onaylama'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    ilk_liste.onay_kaldir(request.user)
    return JsonResponse({'status': 'success', 'message': 'İlk liste bildirimi onayı kaldırıldı.'})

```

---

### Dosya: views\imza_cizelgeleri_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\imza_cizelgeleri_views.py`

```python
from datetime import date
import calendar
import io

from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage

import pdfkit

from mercis657.models import PersonelListesi, PersonelListesiKayit, Mesai, Birim


# PDFKit yapılandırması (Windows varsayılan kurulum yolu)
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')


def imza_cizelgeleri_yazdir(request):
    include_mesai = request.GET.get("mesai", "false") == "true"

    try:
        current_year = int(request.GET.get("year"))
        current_month = int(request.GET.get("month"))
    except Exception:
        return HttpResponseBadRequest("Geçersiz yıl/ay")

    birim_id = request.GET.get('birim')
    if not birim_id:
        return HttpResponseBadRequest("birim parametresi zorunludur")

    try:
        liste = PersonelListesi.objects.get(birim_id=birim_id, yil=current_year, ay=current_month)
    except PersonelListesi.DoesNotExist:
        return HttpResponseBadRequest("İstenen dönem ve birim için PersonelListesi bulunamadı")

    # Logo ve üstbilgi
    try:
        file_url = f"file:///{staticfiles_storage.path('logo/kdh_logo.png')}"
    except Exception:
        file_url = None

    header_ctx = {
        'dokuman_kodu': 'KU.FR.06',
        'form_adi': 'Personel Günlük İmza Cetveli',
        'yayin_tarihi': 'Haziran 2018',
        'kurum': 'KAYSERİ DEVLET HASTANESİ',
        'revizyon_tarihi': 'Mart 2026',
        'revizyon_no': '04',
        'sayfa_no': '1',
        'pdf_logo': file_url,
    }

    # Günler
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = [date(current_year, current_month, d) for d in range(1, days_in_month + 1)]
    birim = Birim.objects.get(BirimID=birim_id)

    # Personeller
    kayitlar = (
        PersonelListesiKayit.objects
        .filter(liste=liste)
        .select_related('personel')
        .order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname')
    )

    pages = []
    for kayit in kayitlar:
        mesai_data = {}
        if include_mesai:
            mesailer = Mesai.objects.filter(Personel=kayit.personel, MesaiDate__year=current_year, MesaiDate__month=current_month).select_related('MesaiTanim')
            for m in mesailer:
                key = m.MesaiDate.strftime('%Y-%m-%d')
                mesai_data[key] = m.MesaiTanim.Saat if m.MesaiTanim else ""

        html_content = render_to_string("mercis657/pdf/imza_cizelgesi.html", {
            "personel": kayit.personel,
            "days": days,
            "mesai_data": mesai_data,
            "birim": birim,
            **header_ctx
        })
        pages.append(html_content)

    # Sayfaları sayfa kırımı ile birleştir (her personel ayrı A4)
    page_break = '<div style="page-break-after: always;"></div>'
    full_html = page_break.join(pages)

    options = {
        'page-size': 'A4',
        'orientation': 'Portrait',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': '',
        'enable-external-links': True,
        'quiet': ''
    }

    pdf = pdfkit.from_string(full_html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="imza_cizelgeleri_{current_year}_{current_month}.pdf"'
    return response



```

---

### Dosya: views\izin_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\izin_views.py`

```python
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Izin
import json
from django.contrib import messages

@require_POST
def izin_ekle(request):
    # Basit yetki kontrolü; gerekiyorsa değiştirin
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz'}, status=403)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        ad = payload.get('ad', '').strip()
        kod_raw = payload.get('kod', None)
        # normalize kod: boş -> None, sayısal -> int, değilse string
        kod = None
        if kod_raw is not None:
            kod_s = str(kod_raw).strip()
            if kod_s != '':
                try:
                    kod = int(kod_s)
                except ValueError:
                    kod = kod_s

        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Ad boş olamaz.'})
        # benzersizlik kontrolleri
        if Izin.objects.filter(ad__iexact=ad).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad ile izin zaten mevcut.'})

        izin = Izin.objects.create(ad=ad, kod=kod)
        messages.success(request, f"{ad} izni başarıyla eklendi.")
        return JsonResponse({'status': 'success', 'id': izin.id, 'kod': izin.kod})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def izin_guncelle(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz'}, status=403)
    izin = get_object_or_404(Izin, pk=pk)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        ad = payload.get('ad', '').strip()
        kod_raw = payload.get('kod', None)
        kod = None
        if kod_raw is not None:
            kod_s = str(kod_raw).strip()
            if kod_s != '':
                try:
                    kod = int(kod_s)
                except ValueError:
                    kod = kod_s

        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Ad boş olamaz.'})
        # çakışma kontrolleri (kendisi hariç)
        if Izin.objects.filter(ad__iexact=ad).exclude(pk=izin.pk).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad başka bir kayıtta kullanılıyor.'})

        izin.ad = ad
        izin.kod = kod
        izin.save()
        return JsonResponse({'status': 'success', 'id': izin.id, 'kod': izin.kod})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
```

---

### Dosya: views\liste_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\liste_views.py`

```python
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from ..models import Birim, PersonelListesi, PersonelListesiKayit

def has_list_management_permission(user):
    return user.has_permission('ÇS 657 Personel Liste Yönetimi')

@login_required
def birim_listeleri(request, birim_id):
    if not has_list_management_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    birim = get_object_or_404(Birim, BirimID=birim_id)
    listeler = PersonelListesi.objects.filter(birim=birim).values('id', 'ay', 'yil')
    return JsonResponse({'listeler': list(listeler)})

@login_required
def liste_personeller(request, liste_id):
    if not has_list_management_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    # The Personel model uses fields PersonelID, PersonelName, PersonelSurname
    personeller_qs = liste.kayitlar.select_related('personel').all().values(
        'personel__PersonelID', 'personel__PersonelName', 'personel__PersonelSurname'
    )
    return JsonResponse({
        'personeller': [
            {
                'id': p['personel__PersonelID'],
                'ad': p['personel__PersonelName'],
                'soyad': p['personel__PersonelSurname']
            }
            for p in personeller_qs
        ]
    })

@login_required
@require_http_methods(["POST"])
def personel_cikar(request, liste_id, personel_id):
    if not has_list_management_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        kayit = PersonelListesiKayit.objects.get(
            liste_id=liste_id,
            personel_id=personel_id
        )
        kayit.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Personel listeden çıkarıldı.'
        })
    except PersonelListesiKayit.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Kayıt bulunamadı.'
        }, status=404)

@login_required
@require_http_methods(["DELETE"])
def liste_sil(request, liste_id):
    if not has_list_management_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    
    if liste.kayitlar.exists():
        return JsonResponse({
            'status': 'error',
            'message': 'Liste içinde personel bulunduğu için silinemez.'
        }, status=400)
    
    birim_id = liste.birim_id
    liste.delete()
    return JsonResponse({
        'status': 'success',
        'message': 'Liste başarıyla silindi.',
        'birim_id': birim_id
    })
```

---

### Dosya: views\main_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\main_views.py`

```python
from mercis657.models import YarimZamanliCalisma
from io import BytesIO
import os
from django.db import IntegrityError
import pandas as pd
from openpyxl import load_workbook, Workbook
import calendar
from datetime import datetime, timedelta, date
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from PersonelYonSis import settings
from ..models import Birim, Mesai, Mesai_Tanimlari, Personel, PersonelListesi, PersonelListesiKayit, UserBirim, Kurum, UstBirim, Idareci, Izin, ResmiTatil, IlkListe, SabitMesai, UserMesaiFavori
from ..utils import get_favori_mesailer
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import locale
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from ..valuelists import CKYS_BTF_VALUES
from ..forms import MesaiTanimForm, ResmiTatilForm, YarimZamanliCalismaForm
User = get_user_model()
try:
    # Windows için
    locale.setlocale(locale.LC_ALL, 'turkish')
except locale.Error:
    try:
        # Linux/Unix için
        locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    except locale.Error:
        # Hiçbiri çalışmazsa varsayılan locale kullan
        locale.setlocale(locale.LC_ALL, '')
from django.conf import settings

def excel_export(request):
    current_year = int(request.GET.get('year', datetime.now().year))
    current_month = int(request.GET.get('month', datetime.now().month))

    df = pd.DataFrame(columns=["Personel Adı", "Personel Unvanı"])

    personeller = Personel.objects.all()
    mesailer = Mesai.objects.filter(MesaiDate__year=current_year, MesaiDate__month=current_month)

    rows = []
    for personel in personeller:
        personel.mesai_data = mesailer.filter(Personel=personel)
        row = {
            "Personel Adı": f"{personel.PersonelName} {personel.PersonelSurname}",
            "Personel Unvanı": personel.PersonelTitle
        }
        for mesai in personel.mesai_data:
            row[mesai.MesaiDate.strftime("%Y-%m-%d")] = mesai.MesaiData
        rows.append(row)

    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

    template_path = os.path.join(settings.STATIC_ROOT, 'excels', 'cizelgeSablon1.xlsx')
    
    with BytesIO() as buffer:
        try:
            if os.path.exists(template_path):
                # Şablon varsa yükle
                book = load_workbook(template_path)
            else:
                # Şablon yoksa yeni bir Workbook oluştur
                book = Workbook()

            # Çalışma sayfası olup olmadığını kontrol et
            if not book.worksheets:
                book.create_sheet(title="Mesai Verileri")

            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                writer.book = book
                writer.sheets = {ws.title: ws for ws in book.worksheets}

                # Veriyi A2 hücresinden itibaren yazdır
                df.to_excel(writer, index=False, startrow=1, sheet_name='Mesai Verileri')

                # Başlık ekle
                sheet = writer.sheets['Mesai Verileri']
                sheet['A1'] = f"{current_year} - {current_month} dönemi Mesai verileri"

            # Yazdırma işlemi
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'inline; filename="{current_year}_{current_month}_mesai_verileri.xlsx"'
            return response

        except Exception as e:
            return HttpResponse(f"Hata oluştu: {str(e)}", status=500)

@login_required
def cizelge(request):
    user = request.user
    tum_birimler_yetkisi = request.user.has_permission("ÇS 657 Tüm Birimleri Görebilir")
    user_birim_ids = list(UserBirim.objects.filter(user=user).values_list('birim__BirimID', flat=True))

    if tum_birimler_yetkisi:
        birimler = Birim.objects.select_related('Kurum', 'UstBirim', 'Idareci').all().order_by('BirimAdi')
    else:
        birimler = Birim.objects.filter(BirimID__in=user_birim_ids).select_related('Kurum', 'UstBirim', 'Idareci').order_by('BirimAdi')
    izinler = Izin.objects.all()
    kurumlar = Kurum.objects.all()
    ust_birimler = UstBirim.objects.all()
    idareciler = Idareci.objects.all()
    # Dönemler: mevcut aydan 6 ay önce ile 2 ay sonrası arası
    today = date.today().replace(day=1)
    donemler = []
    for i in range(-6, 5):
        d = today + relativedelta(months=i)
        value = f"{d.year}/{d.month:02d}"
        label = value
        donemler.append({'value': value, 'label': label})

    selected_birim_id = request.GET.get('birim_id') or ""
    selected_donem = request.GET.get('donem') or ""
    
    # Güvenli sabit_mesailer listesi oluştur
    sabit_mesailer = []
    try:
        for sm in SabitMesai.objects.all():
            try:
                # ara_dinlenme değerini kontrol et
                if sm.ara_dinlenme is not None:
                    float(sm.ara_dinlenme)
                sabit_mesailer.append(sm)
            except (ValueError, TypeError):
                # Problemli kayıtları atla
                continue
    except Exception:
        sabit_mesailer = []
    
    # Favori mesai modal için gerekli veriler
    favori_mesailer = UserMesaiFavori.objects.filter(user=user).values_list('mesai_id', flat=True)
    all_mesai_tanimlari = Mesai_Tanimlari.objects.all().order_by('Saat')
    
    pastcontext = {
            "birimler": birimler,
            "selected_birim_id": selected_birim_id,
            "donemler": donemler,
            "selected_donem": selected_donem,
            "mesai_options": get_favori_mesailer(user),
            "sabit_mesailer": sabit_mesailer,  # Modal için eklendi
            "kurumlar": kurumlar,
            "ust_birimler": ust_birimler,
            "idareciler": idareciler,
            "izinler": izinler,
            "all_mesai_tanimlari": all_mesai_tanimlari,
            "favori_ids": list(favori_mesailer),
        }
    # Eğer GET ile birim ve dönem seçilmemişse, context'e sadece seçim listelerini gönder
    if not selected_birim_id or not selected_donem:
        return render(request, 'mercis657/cizelge.html', pastcontext)
    # Dönem bilgisini parse et ("YYYY/MM" formatı)
    try:
        current_year, current_month = map(int, selected_donem.split('/'))
    except Exception:
        messages.warning(request, "Geçersiz dönem formatı.")
        return render(request, 'mercis657/cizelge.html', pastcontext)

    birim_id = selected_birim_id

    if not birim_id:
        messages.warning(request, "Lütfen bir birim seçiniz.")
        return render(request, 'mercis657/cizelge.html', pastcontext)

    birim = get_object_or_404(Birim, BirimID=birim_id)

    if not tum_birimler_yetkisi and not UserBirim.objects.filter(user=request.user, birim=birim).exists() and not (request.user.has_permission('ÇS 657 Tüm Listeleri Düzenleyebilir')):
        return HttpResponseForbidden("Bu birim için yetkiniz yok.")

    # Liste varsa getir
    try:
        liste = PersonelListesi.objects.get(birim=birim, yil=current_year, ay=current_month)
    except PersonelListesi.DoesNotExist:
        messages.warning(request, f"{current_month}/{current_year} için personel listesi oluşturulmamış.")
        return render(request, 'mercis657/cizelge.html', pastcontext)

    # Sıralı personel listesi
    kayitlar = PersonelListesiKayit.objects.filter(liste=liste).select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname')
    personeller = [k.personel for k in kayitlar]
    mesai_tanimlari = get_favori_mesailer(user)
    mesailer = Mesai.objects.filter(
        Personel__in=personeller,
        MesaiDate__year=current_year,
        MesaiDate__month=current_month
    ).select_related('MesaiTanim', 'Izin').prefetch_related('yedekler', 'mercis657_stoplar', 'mercis657_ek_mesailer')

    # Resmi tatilleri al
    resmi_tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=current_year,
        TatilTarihi__month=current_month
    ).values_list('TatilTarihi', flat=True)
    
    # Gün listesi
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = [
        {
            'full_date': f"{current_year}-{current_month:02}-{day:02}",
            'day_num': day,
            'is_weekend': calendar.weekday(current_year, current_month, day) >= 5,
            'is_resmi_tatil': f"{current_year}-{current_month:02}-{day:02}" in [t.strftime('%Y-%m-%d') for t in resmi_tatiller]
        }
        for day in range(1, days_in_month + 1)
    ]

    # Personel mesai eşleme
    mesai_map = {}
    for mesai in mesailer:
        key = f"{mesai.Personel.PersonelID}_{mesai.MesaiDate.strftime('%Y-%m-%d')}"
        last_backup = mesai.yedekler.order_by('-created_at').first()
        # get latest stop if any
        last_stop = None
        try:
            last_stop = mesai.mercis657_stoplar.order_by('-created_at').first()
        except Exception:
            last_stop = None

        mesai_map[key] = {
            "MesaiID": mesai.MesaiID,
            "MesaiTanimID": mesai.MesaiTanim.id if mesai.MesaiTanim else None,
            "MesaiTanimRenk": mesai.MesaiTanim.Renk if mesai.MesaiTanim else None,
            "IzinID": mesai.Izin.id if mesai.Izin else None,
            "SistemdekiIzin": mesai.SistemdekiIzin,
            "MesaiNotu": mesai.MesaiNotu,
            "Saat": mesai.MesaiTanim.Saat if mesai.MesaiTanim else "",
            "IzinAd": mesai.Izin.ad if mesai.Izin else "",
            "Degisiklik": mesai.Degisiklik,
            "PrevSaat": (last_backup.MesaiTanim.Saat if (last_backup and last_backup.MesaiTanim) else ""),
            "PrevIzinAd": (last_backup.Izin.ad if (last_backup and last_backup.Izin) else ""),
            "Icap": mesai.Icap,
        }

        if last_stop:
            # format datetimes for display
            try:
                sb = last_stop.StopBaslangic.strftime('%H:%M')
            except Exception:
                sb = str(last_stop.StopBaslangic)
            try:
                se = last_stop.StopBitis.strftime('%H:%M')
            except Exception:
                se = str(last_stop.StopBitis)

            mesai_map[key]['StopKaydi'] = {
                'StopBaslangic': sb,
                'StopBitis': se,
                'Sure': last_stop.Sure,
                'created_by': str(last_stop.created_by) if last_stop.created_by else '' ,
                'id': last_stop.id
            }
        else:
            mesai_map[key]['StopKaydi'] = None

        # get latest ek mesai if any
        last_ek = None
        try:
            last_ek = mesai.mercis657_ek_mesailer.order_by('-created_at').first()
        except Exception:
            last_ek = None
        
        if last_ek:
            try:
                eb = last_ek.Baslangic.strftime('%H:%M')
            except Exception:
                eb = str(last_ek.Baslangic)
            try:
                ee = last_ek.Bitis.strftime('%H:%M')
            except Exception:
                ee = str(last_ek.Bitis)
            
            mesai_map[key]['EkMesai'] = {
                'Baslangic': eb,
                'Bitis': ee,
                'Sure': last_ek.Sure,
                'Riskli': last_ek.Riskli,
                'id': last_ek.id,
                'created_by': str(last_ek.created_by) if last_ek.created_by else ''
            }
        else:
            mesai_map[key]['EkMesai'] = None

    # Personel nesnesine mesai bilgisi ekleyelim
    for idx, p in enumerate(personeller):
        p.mesai_data = []
        for day in days:
            key = f"{p.PersonelID}_{day['full_date']}"
            mesai_info = mesai_map.get(key, {
                "MesaiID": None,
                "MesaiTanimID": None,
                "IzinID": None,
                "Saat": "",
                "IzinAd": "",
                "Degisiklik": False,
                "PrevSaat": "",
                "PrevIzinAd": "",
                "Icap": False
            })
            mesai_info["MesaiDate"] = day['full_date']
            mesai_info["is_weekend"] = day['is_weekend']
            mesai_info["is_resmi_tatil"] = day['is_resmi_tatil']
            p.mesai_data.append(mesai_info)

    # Güvenli sabit_mesailer listesi oluştur
    sabit_mesailer = []
    try:
        for sm in SabitMesai.objects.all():
            try:
                # ara_dinlenme değerini kontrol et
                if sm.ara_dinlenme is not None:
                    float(sm.ara_dinlenme)
                sabit_mesailer.append(sm)
            except (ValueError, TypeError):
                # Problemli kayıtları atla
                continue
    except Exception:
        sabit_mesailer = []
    
    bildirim_yetkisi = request.user.has_permission("ÇS 657 Bildirim İşlemleri")
    
    context = {
        "personeller": personeller,
        "mesai_options": mesai_tanimlari,
        "sabit_mesailer": sabit_mesailer,  # Modal için eklendi
        "izinler": izinler,
        "days": days,
        "birim": birim,
        "current_year": current_year,
        "current_month": current_month,
        "months": [{'value': i, 'label': calendar.month_name[i]} for i in range(1, 13)],
        "years": [year for year in range(2023, 2027)],
        "birimler": birimler,
        "selected_birim_id": selected_birim_id,
        "liste": liste.id if liste else 0,
        "donemler": donemler,
        "all_mesai_tanimlari": all_mesai_tanimlari,
        "favori_ids": list(favori_mesailer),
        "selected_donem": selected_donem,
        "kurumlar": kurumlar,
        "ust_birimler": ust_birimler,
        "idareciler": idareciler,
        "aciklama": liste.aciklama if liste else "",
        "mevcut_personeller": kayitlar,  # Modal için ekledik
        "ilk_liste": IlkListe.objects.filter(PersonelListesi=liste).first() if liste else None,
        "bildirim_yetkisi": bildirim_yetkisi,
    }
    return render(request, 'mercis657/cizelge.html', context)

@login_required
@require_POST
def yarim_zamanli_calisma_kaydet(request, personel_id):
    personel = get_object_or_404(Personel, pk=personel_id)
    form = YarimZamanliCalismaForm(request.POST)

    if form.is_valid():
        yz = form.save(commit=False)
        bas = yz.baslangic_tarihi
        bit = yz.bitis_tarihi
        
        cakisan = False
        for mevcut in YarimZamanliCalisma.objects.filter(personel=personel):
            m_bas = mevcut.baslangic_tarihi
            m_bit = mevcut.bitis_tarihi
            if not bit and not m_bit:
                cakisan = True; break
            if not bit:
                if m_bit and bas <= m_bit:
                    cakisan = True; break
            elif not m_bit:
                if bit >= m_bas:
                    cakisan = True; break
            else:
                if bas <= m_bit and bit >= m_bas:
                    cakisan = True; break
        
        if cakisan:
            return JsonResponse({"status": "error", "errors": "Bu tarihler arasında sistemde aktif veya çakışan bir yarım zamanlı çalışma kaydı bulunmaktadır!"})

        yz.personel = personel
        yz.haftalik_plan = json.loads(request.POST.get("haftalik_plan", "{}"))
        yz.save()
        messages.success(request, "Kayıt başarıyla kaydedildi!")
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "errors": str(form.errors)})


@login_required
@require_POST
def yarim_zamanli_calisma_sil(request, pk):
    try:
        yz = get_object_or_404(YarimZamanliCalisma, pk=pk)
        yz.delete()
        return JsonResponse({"status": "success", "message": "Kayıt başarıyla silindi."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})


@login_required
def personel_listeleri(request):
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim_id', flat=True)
    birimler = Birim.objects.filter(id__in=user_birimler)
    listeler = PersonelListesi.objects.filter(birim__in=birimler).order_by('-yil', '-ay')
    return render(request, 'mercis657/personel_listeleri.html', {
        'birimler': birimler,
        'listeler': listeler
    })

@login_required
def personel_listesi_olustur(request):
    if request.method == 'POST':
        birim_id = request.POST.get('birim_id')
        yil = int(request.POST.get('yil'))
        ay = int(request.POST.get('ay'))

        birim = get_object_or_404(Birim, id=birim_id)

        if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
            return HttpResponseForbidden('Bu birim için yetkiniz yok.')

        try:
            liste, created = PersonelListesi.objects.get_or_create(birim=birim, yil=yil, ay=ay)
            if created:
                messages.success(request, 'Personel listesi oluşturuldu.')
            else:
                messages.warning(request, 'Bu ay ve birim için liste zaten var.')
        except IntegrityError:
            messages.error(request, 'Liste oluşturulurken bir hata oluştu.')

        return redirect('mercis657:personel_listeleri')

@login_required
def personel_listesi_detay(request, liste_id):
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    if not request.user.has_permission("ÇS 657 Tüm Birimleri Görebilir"):
        if not UserBirim.objects.filter(user=request.user, birim=liste.birim).exists():
            return HttpResponseForbidden('Bu listeye erişim yetkiniz yok.')

    mevcut_personeller = PersonelListesiKayit.objects.filter(personel_listesi=liste).select_related('personel').order_by('sira_no', 'personel__FirstName', 'personel__LastName')
    tum_personeller = Personel.objects.all().order_by('FirstName', 'LastName')

    return render(request, 'mercis657/personel_listesi_detay.html', {
        'liste': liste,
        'mevcut_personeller': mevcut_personeller,
        'tum_personeller': tum_personeller
    })

@login_required
def tanimlamalar(request):
    kurumlar = Kurum.objects.all()
    ust_birimler = UstBirim.objects.all()
    idareciler = Idareci.objects.all()
    izinler = Izin.objects.all()
    mesai_tanimlari = Mesai_Tanimlari.objects.all().order_by('Saat')
    mesai_form = MesaiTanimForm()
    resmi_tatil_form = ResmiTatilForm()
    tatiller = ResmiTatil.objects.all().order_by('TatilTarihi')
    return render(request, "mercis657/tanimlamalar.html", {
        "kurumlar": kurumlar,
        "ust_birimler": ust_birimler,
        "idareciler": idareciler,
        "izinler": izinler,
        "mesai_tanimlari": mesai_tanimlari,
        "form": mesai_form,
        "rt_form": resmi_tatil_form,
        "tatiller": tatiller
    })

@require_POST
@login_required
def personel_cikar(request, liste_id, personel_id):
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    if not request.user.has_permission("ÇS 657 Tüm Birimleri Görebilir"):
        if not UserBirim.objects.filter(user=request.user, birim=liste.birim).exists():
            return JsonResponse({'status': 'error', 'message': 'Yetkisiz işlem.'}, status=403)

    try:
        kayit = get_object_or_404(PersonelListesiKayit, liste=liste, personel_id=personel_id)
        kayit.delete()
        return JsonResponse({'status': 'success', 'message': 'Personel listeden çıkarıldı.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def onceki_donem_personel(request, donem, birim_id):
    """
    Bir önceki döneme ait personelleri getir (PersonelListesi ve PersonelListesiKayit üzerinden)
    """
    # Yetki kontrolü
    if not UserBirim.objects.filter(user=request.user, birim__BirimID=birim_id).exists():
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
    try:
        # donem: "YYYY-MM" veya "YYYY/MM"
        if '-' in donem:
            year, month = map(int, donem.split('-'))
        elif '/' in donem:
            year, month = map(int, donem.split('/'))
        else:
            raise Exception("Dönem formatı hatalı")
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1

        # Önceki dönem personel listesi
        liste = PersonelListesi.objects.filter(birim__BirimID=birim_id, yil=prev_year, ay=prev_month).first()
        if not liste:
            return JsonResponse([], safe=False)

        kayitlar = PersonelListesiKayit.objects.filter(liste=liste).select_related('personel')
        data = [{
            'personel_id': k.personel.PersonelID,
            'tc_kimlik': getattr(k.personel, 'PersonelTCKN', ''),
            'adi': getattr(k.personel, 'PersonelName', ''),
            'soyadi': getattr(k.personel, 'PersonelSurname', ''),
            'unvan': getattr(k.personel, 'PersonelTitle', '')
        } for k in kayitlar]

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_POST
@login_required
def liste_aciklama_kaydet(request):
    try:
        data = json.loads(request.body)
        donem = data.get('donem')
        birim_id = data.get('birim_id')
        aciklama = data.get('aciklama', '')
        if not (donem and birim_id):
            return JsonResponse({'status': 'error', 'message': 'Eksik veri.'})
        year, month = map(int, donem.replace('-', '/').split('/'))
        liste = PersonelListesi.objects.filter(birim__BirimID=birim_id, yil=year, ay=month).first()
        if not liste:
            return JsonResponse({'status': 'error', 'message': 'Liste bulunamadı.'})
        liste.aciklama = aciklama
        liste.save(update_fields=['aciklama'])
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
@login_required
def personel_listesi_sira_kaydet(request, liste_id):
    """
    PersonelListesiKayit sıralamasını kaydeder.
    Test için örnek:
    curl -X POST -H "Content-Type: application/json" -H "X-CSRFToken: <token>" \
      -d '{"order":[{"id":123,"sira_no":1},{"id":456,"sira_no":2}]}' \
      http://localhost:8000/mercis657/personel-listesi/1/sira-kaydet/
    """
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    if not request.user.has_permission("ÇS 657 Tüm Birimleri Görebilir"):
        if not UserBirim.objects.filter(user=request.user, birim=liste.birim).exists():
            return HttpResponseForbidden('Yetkisiz işlem.')

    try:
        data = json.loads(request.body)
        order = data.get('order', [])
        if not isinstance(order, list):
            return JsonResponse({'status': 'error', 'message': 'Geçersiz veri.'}, status=400)
        # id'leri int'e çevir
        id_list = []
        id_to_sira = {}
        for item in order:
            if not isinstance(item, dict) or 'id' not in item or 'sira_no' not in item:
                return JsonResponse({'status': 'error', 'message': 'Her eleman id ve sira_no içermeli.'}, status=400)
            try:
                int_id = int(item['id'])
            except Exception:
                return JsonResponse({'status': 'error', 'message': 'ID değeri sayı olmalı.'}, status=400)
            id_list.append(int_id)
            id_to_sira[int_id] = int(item['sira_no'])

        kayit_objs = list(PersonelListesiKayit.objects.filter(id__in=id_list, liste=liste))
        if len(kayit_objs) != len(order):
            return JsonResponse({'status': 'error', 'message': 'Bazı kayıtlar bulunamadı veya yetkisiz.'}, status=400)
        # id->obj map
        id_to_obj = {k.id: k for k in kayit_objs}
        # Sıra numaralarını güncelle
        for int_id in id_list:
            obj = id_to_obj.get(int_id)
            if obj:
                obj.sira_no = id_to_sira[int_id]
        # Bulk update
        with transaction.atomic():
            PersonelListesiKayit.objects.bulk_update(kayit_objs, ['sira_no'])
            # Normalize: Sıra numaralarını 1..N olarak düzelt (opsiyonel)
            all_kayitlar = list(PersonelListesiKayit.objects.filter(liste=liste).order_by('sira_no', 'id'))
            for idx, k in enumerate(all_kayitlar, start=1):
                k.sira_no = idx
            PersonelListesiKayit.objects.bulk_update(all_kayitlar, ['sira_no'])
        return JsonResponse({'status': 'success', 'updated': len(kayit_objs)})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def favori_mesai_kaydet(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Geçersiz istek."}, status=400)

    mesai_ids = json.loads(request.body.decode("utf-8")).get("mesai_ids", [])
    UserMesaiFavori.objects.filter(user=request.user).delete()

    for mid in mesai_ids:
        UserMesaiFavori.objects.create(user=request.user, mesai_id=mid)

    return JsonResponse({"status": "success"})

@login_required
@require_GET
def onceki_ay_siralamasi(request, liste_id):
    """
    Bir önceki ayın personel sıralamasını getirir.
    PersonelListesiKayit modelinden personelin bir önceki aya ait sira_no bilgisini döndürür.
    """
    liste = get_object_or_404(PersonelListesi, id=liste_id)
        
    try:
        # Önceki ayı hesapla
        current_year = liste.yil
        current_month = liste.ay
        
        if current_month == 1:
            prev_year = current_year - 1
            prev_month = 12
        else:
            prev_year = current_year
            prev_month = current_month - 1
        
        # Önceki ayın listesini bul
        prev_liste = PersonelListesi.objects.filter(
            birim=liste.birim,
            yil=prev_year,
            ay=prev_month
        ).first()
        
        if not prev_liste:
            return JsonResponse({
                'status': 'error',
                'message': 'Önceki ay için liste bulunamadı.'
            }, status=404)
        
        # Önceki ayın kayıtlarını al (personel_id -> sira_no mapping)
        prev_kayitlar = PersonelListesiKayit.objects.filter(
            liste=prev_liste
        ).select_related('personel').order_by('sira_no')
        
        # Mapping oluştur: personel_id -> sira_no
        siralamasi = {}
        for kayit in prev_kayitlar:
            if kayit.sira_no is not None:
                siralamasi[kayit.personel.PersonelID] = kayit.sira_no
        
        return JsonResponse({
            'status': 'success',
            'siralamasi': siralamasi,
            'prev_year': prev_year,
            'prev_month': prev_month
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


```

---

### Dosya: views\mazeret_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\mazeret_views.py`

```python
import calendar
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from datetime import datetime
import json
from ..models import Personel, PersonelListesi, PersonelListesiKayit, MazeretKaydi, Mesai, Mesai_Tanimlari, ResmiTatil
from ..utils import hesapla_fazla_mesai

@login_required
@require_POST
def mazeret_ekle(request):
    """Yeni mazeret kaydı ekler"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        personel_id = data.get('personel_id')
        baslangic_tarihi = data.get('baslangic_tarihi')
        bitis_tarihi = data.get('bitis_tarihi')
        gunluk_azaltim_saat = data.get('gunluk_azaltim_saat')
        aciklama = data.get('aciklama', '')
        
        if not all([personel_id, baslangic_tarihi, bitis_tarihi, gunluk_azaltim_saat]):
            return JsonResponse({'status': 'error', 'message': 'Tüm alanlar doldurulmalı.'})
        
        personel = get_object_or_404(Personel, pk=personel_id)

        # Aynı tarihlerde çakışan mazeret kontrolü
        mevcut_mazeretler = MazeretKaydi.objects.filter(
            personel=personel,
            baslangic_tarihi__lte=bitis_tarihi,
            bitis_tarihi__gte=baslangic_tarihi
        )
        if mevcut_mazeretler.exists():
            return JsonResponse({'status': 'error', 'message': 'Bu tarihlerde zaten bir mazeret kaydı mevcut.'})
                
        mazeret = MazeretKaydi.objects.create(
            personel=personel,
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi,
            gunluk_azaltim_saat=gunluk_azaltim_saat,
            aciklama=aciklama,
            created_by=request.user
        )
        messages.success(request, f"{personel.PersonelName} için yeni mazeret kaydı eklendi.")
        return JsonResponse({
            'status': 'success',
            'message': 'Mazeret kaydı eklendi.',
            'mazeret_id': mazeret.id
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def mazeret_guncelle(request, mazeret_id):
    """Mazeret kaydını günceller"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        mazeret = get_object_or_404(MazeretKaydi, pk=mazeret_id)
        data = json.loads(request.body)
        
        mazeret.baslangic_tarihi = data.get('baslangic_tarihi', mazeret.baslangic_tarihi)
        mazeret.bitis_tarihi = data.get('bitis_tarihi', mazeret.bitis_tarihi)
        mazeret.gunluk_azaltim_saat = data.get('gunluk_azaltim_saat', mazeret.gunluk_azaltim_saat)
        mazeret.aciklama = data.get('aciklama', mazeret.aciklama)
        mazeret.save()
        
        messages.success(request, f"{mazeret.personel.PersonelName} için mazeret kaydı güncellendi.")
        return JsonResponse({'status': 'success', 'message': 'Mazeret kaydı güncellendi.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def mazeret_sil(request, mazeret_id):
    """Mazeret kaydını siler"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        mazeret = get_object_or_404(MazeretKaydi, pk=mazeret_id)
        mazeret.delete()
        
        messages.success(request, f"{mazeret.personel.PersonelName} için mazeret kaydı silindi.")
        return JsonResponse({'status': 'success', 'message': 'Mazeret kaydı silindi.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def radyasyon_toggle(request, personel_id, liste_id):
    """Personelin radyasyon çalışanı durumunu değiştirir"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        kayit = get_object_or_404(PersonelListesiKayit, personel_id=personel_id, liste_id=liste_id)
        kayit.radyasyon_calisani = not kayit.radyasyon_calisani
        kayit.save()
        
        messages.success(request, f"{kayit.personel.PersonelName} için radyasyon çalışanı durumu güncellendi.")
        return JsonResponse({
            'status': 'success',
            'message': 'Radyasyon çalışanı durumu güncellendi.',
            'radyasyon_calisani': kayit.radyasyon_calisani
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


```

---

### Dosya: views\mesai_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\mesai_views.py`

```python
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Mesai_Tanimlari
from ..forms import MesaiTanimForm
from datetime import timedelta
from .main_views import tanimlamalar

# Yeni Mesai Tanımı Ekleme Fonksiyonu
def add_mesai_tanim(request):
    if request.method == 'POST':
        form = MesaiTanimForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            # Renk siyah veya boş ise None kaydet
            renk = form.cleaned_data.get('Renk')
            if not renk or renk.lower() == '#000000':
                obj.Renk = None
            obj.calculate_sure()
            obj.save()
            messages.success(request, "Mesai kaydı eklendi")
            return redirect('mercis657:tanimlamalar')
        # Geçersiz ise aynı sayfayı form hatalarıyla render et
        tanimlamalar(request)
    return redirect('mercis657:tanimlamalar')

def mesai_tanim_update(request):
    mesai_id = request.POST.get('mesai_id')
    mesai = get_object_or_404(Mesai_Tanimlari, id=mesai_id)
    if request.method == 'POST':
        form = MesaiTanimForm(request.POST, instance=mesai)
        if form.is_valid():
            obj = form.save(commit=False)
            renk = form.cleaned_data.get('Renk')
            if not renk or renk.lower() == '#000000':
                obj.Renk = None
            obj.calculate_sure()
            obj.save()
            return JsonResponse({'status': 'success'})
        # Form hatalarını döndür
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'}, status=405)

@login_required
def mesai_tanim_form(request, pk):
    """Modal için form HTML döndürür (edit)."""
    mesai = get_object_or_404(Mesai_Tanimlari, pk=pk)
    form = MesaiTanimForm(instance=mesai)
    return render(request, 'mercis657/_mesai_tanim_form.html', {
        'form': form,
        'mesai': mesai,
    })
def delete_mesai_tanim(request):
    if request.method == 'POST':
        mesai_id = request.POST.get('mesai_id')
        try:
            mesai = get_object_or_404(Mesai_Tanimlari, id=mesai_id)
            mesai.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})

```

---

### Dosya: views\personel_islem_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\personel_islem_views.py`

```python
from tkinter import Y
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import datetime, date
import json

from mercis657.views.main_views import yarim_zamanli_calisma_kaydet
from ..models import Personel, PersonelListesi, PersonelListesiKayit, Mesai, Mesai_Tanimlari, ResmiTatil, MazeretKaydi, SabitMesai, YarimZamanliCalisma, UserMesaiFavori
from ..utils import hesapla_fazla_mesai, get_favori_mesailer


@login_required
@require_POST
def hazir_mesai_ata(request, personel_id, liste_id, year, month):
    """Seçilen günlere hazır mesai atar"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        mesai_tanim_id = data.get('mesai_tanim_id')
        gunler = data.get('gunler', [])  # [1, 5, 10] gibi gün numaraları
        
        if not mesai_tanim_id or not gunler:
            return JsonResponse({'status': 'error', 'message': 'Mesai tanımı ve günler seçilmelidir.'})
        
        personel = get_object_or_404(Personel, pk=personel_id)
        mesai_tanim = get_object_or_404(Mesai_Tanimlari, pk=mesai_tanim_id)
                
        created_count = 0
        
        for gun_no in gunler:
            current_date = date(year, month, gun_no)
            
            # Bu güne zaten mesai var mı kontrol et
            existing = Mesai.objects.filter(
                Personel=personel,
                MesaiDate=current_date
            ).first()
            
            if not existing:
                Mesai.objects.create(
                    Personel=personel,
                    MesaiDate=current_date,
                    MesaiTanim=mesai_tanim,
                    OnayDurumu=True,
                    Degisiklik=False
                )
                created_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} güne mesai atandı.',
            'created_count': created_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def personel_profil(request, personel_id, liste_id, year, month):
    """Personel profil modalını döner"""
    personel = get_object_or_404(Personel, pk=personel_id)
    liste = get_object_or_404(PersonelListesi, pk=liste_id)
    user = request.user
    # Tüm Sabit mesaileri çekiyoruz - güvenli şekilde
    try:
        # Problemli ara_dinlenme değerlerini filtrele
        sabit_mesailer = []
        for sm in SabitMesai.objects.all():
            try:
                # ara_dinlenme değerini kontrol et
                if sm.ara_dinlenme is not None:
                    float(sm.ara_dinlenme)
                sabit_mesailer.append(sm)
            except (ValueError, TypeError):
                # Problemli kayıtları atla
                continue
    except Exception as e:
        # Eğer veritabanında problem varsa boş liste döndür
        sabit_mesailer = []

    kayit, created = PersonelListesiKayit.objects.get_or_create(
        liste=liste,
        personel=personel,
        defaults={'radyasyon_calisani': False}
    )

    mazeret_kayitlari = MazeretKaydi.objects.filter(
        personel=personel
    ).order_by('-baslangic_tarihi')

    yarim_zamanli_calismalar = YarimZamanliCalisma.objects.filter( personel=personel ).order_by('-baslangic_tarihi')
    yarim_zamanli_calisma = yarim_zamanli_calismalar.first()

    # year ve month'u integer'a çevir
    year = int(year)
    month = int(month)
    
    hesaplama = hesapla_fazla_mesai(kayit, year, month)
    mesai_tanimlari = get_favori_mesailer(user)

    # Onaylı mesaileri disable et
    onayli_mesailer = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month,
        OnayDurumu=True
    )
    disabled_days = [m.MesaiDate.day for m in onayli_mesailer]

    # Resmi tatil ve arefeler
    tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year, TatilTarihi__month=month
    )
    resmi_tatil_gunleri = [
        t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM'
    ]
    arefe_gunleri = [
        t.TatilTarihi.day for t in tatiller if t.ArefeMi
    ]
    
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    
    context = {
        'personel': personel,
        'sabit_mesailer' : sabit_mesailer,
        'gunler': gunler,
        'liste': liste,
        'kayit': kayit,
        'mazeret_kayitlari': mazeret_kayitlari,
        'yarim_zamanli_calismalar': yarim_zamanli_calismalar,
        'yarim_zamanli_calisma': yarim_zamanli_calisma,
        'hesaplama': hesaplama,
        'mesai_tanimlari': mesai_tanimlari,
        'year': year,
        'month': month,
        'resmi_tatil_gunleri': resmi_tatil_gunleri,
        'arefe_gunleri': arefe_gunleri,
        'disabled_days': disabled_days,
        'hazir_mesai_ata_url': reverse(
            'mercis657:hazir_mesai_ata',
            args=[personel.PersonelID, liste.id, year, month]
        ),
        'extra_payload': {   # 🔑 toplu_islem ile uyumlu hale getiriyoruz
            'personel_id': personel.PersonelID,
            'liste_id': liste.id
        },
    }
    return render(request, 'mercis657/personel_profil.html', context)


@login_required
@require_POST
def sabit_mesai_guncelle(request):
    """Sabit mesai güncelleme endpoint'i"""
    try:
        data = json.loads(request.body)
        personel_id = data.get('personel_id')
        liste_id = data.get('liste_id')
        sabit_mesai_id = data.get('sabit_mesai_id')
        
        if not personel_id or not liste_id:
            return JsonResponse({'status': 'error', 'message': 'Personel ID ve Liste ID gerekli'})
        
        # Personel ve liste kontrolü
        personel = get_object_or_404(Personel, pk=personel_id)
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        
        # PersonelListesiKayit'ı bul veya oluştur
        kayit, created = PersonelListesiKayit.objects.get_or_create(
            liste=liste,
            personel=personel,
            defaults={'radyasyon_calisani': False}
        )
        
        # Sabit mesai güncelle
        if sabit_mesai_id:
            sabit_mesai = get_object_or_404(SabitMesai, pk=sabit_mesai_id)
            kayit.sabit_mesai = sabit_mesai
        else:
            kayit.sabit_mesai = None
            
        kayit.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Sabit mesai başarıyla güncellendi'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Hata oluştu: {str(e)}'
        })


@login_required
@require_POST
def toplu_sabit_mesai_ata(request, liste_id):
    """Tüm personele sabit mesai durumu atar"""
    try:
        data = json.loads(request.body)
        sabit_mesai_id = data.get('sabit_mesai_id')
        
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        
        # Sabit mesai kontrolü
        sabit_mesai = None
        if sabit_mesai_id:
            sabit_mesai = get_object_or_404(SabitMesai, pk=sabit_mesai_id)
        
        # Tüm personel kayıtlarını güncelle
        updated_count = PersonelListesiKayit.objects.filter(
            liste=liste
        ).update(sabit_mesai=sabit_mesai)
        
        sabit_mesai_text = sabit_mesai.aralik if sabit_mesai else "Hiçbiri"
        
        return JsonResponse({
            'status': 'success',
            'message': f'{updated_count} personelin sabit mesai durumu "{sabit_mesai_text}" olarak güncellendi.',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Hata oluştu: {str(e)}'
        })


@login_required
@login_required
def get_calisma_statusu_list(request, liste_id):
    """Personel listesindeki kayıtları ve çalışma statülerini döner. liste_id parametresi birim_id olarak da kullanılabilir."""
    try:
        year = request.GET.get('year')
        month = request.GET.get('month')
        
        # Eğer yıl ve ay parametreleri varsa, liste_id aslında birim_id'dir.
        if year and month:
            # İlgili birim ve dönem için listeyi bul
            liste = PersonelListesi.objects.filter(
                birim_id=liste_id, 
                yil=year, 
                ay=month
            ).first()
            
            if not liste:
                 return JsonResponse({'status': 'error', 'message': f'{year}/{month} dönemi için personel listesi bulunamadı.'}, status=404)
        else:
            # Direkt liste ID olarak işlem yap
            liste = get_object_or_404(PersonelListesi, pk=liste_id)

        kayitlar = liste.kayitlar.select_related('personel').all().order_by('sira_no', 'personel__PersonelName')
        
        data = []
        for k in kayitlar:
            data.append({
                'personel_id': k.personel.PersonelID,
                'ad_soyad': f"{k.personel.PersonelName} {k.personel.PersonelSurname}",
                'is_gunduz_personeli': k.is_gunduz_personeli
            })
            
        return JsonResponse({'status': 'success', 'data': data, 'actual_liste_id': liste.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def update_calisma_statusu_list(request, liste_id):
    """Personel listesindeki kayıtların çalışma statülerini günceller."""
    try:
        import json
        from .cizelge_kontrol_views import sabit_mesai_kontrol
        
        payload = json.loads(request.body)
        updates = payload.get('updates', []) # List of {personel_id: x, is_gunduz_personeli: bool}
        
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        
        updated_count = 0
        for item in updates:
            pid = item.get('personel_id')
            status = item.get('is_gunduz_personeli')
            
            if pid is not None and status is not None:
                # is_gunduz_personeli alanını güncelle ve eğer False ise sabit_mesai alanını None yap
                if status == False:
                    cnt = PersonelListesiKayit.objects.filter(liste=liste, personel__PersonelID=pid).update(is_gunduz_personeli=status, sabit_mesai=None)
                else:
                    cnt = PersonelListesiKayit.objects.filter(liste=liste, personel__PersonelID=pid).update(is_gunduz_personeli=status)
                updated_count += cnt
        
        # Statüsü True (Gündüz Personeli) olanlar için sabit mesai kontrolünü çalıştır
        if updated_count > 0:
            sabit_mesai_kontrol(liste, int(liste.yil), int(liste.ay))
                
        return JsonResponse({'status': 'success', 'message': f'{updated_count} kayıt güncellendi.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

```

---

### Dosya: views\personel_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\personel_views.py`

```python
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Birim, PersonelListesi, PersonelListesiKayit, Personel
from django.db import transaction

@csrf_exempt
@require_POST
@login_required
def personel_kaydet(request):
    import json
    try:
        data = json.loads(request.body)
        donem = data.get('donem')
        birim_id = data.get('birim_id')
        personeller = data.get('personeller', [])
        if not (donem and birim_id and personeller):
            return JsonResponse({'status': 'error', 'message': 'Eksik veri.'})
        year, month = map(int, donem.replace('-', '/').split('/'))
        birim = Birim.objects.get(BirimID=birim_id)
        with transaction.atomic():
            liste, _ = PersonelListesi.objects.get_or_create(birim=birim, yil=year, ay=month)
            eklenenler = []
            for p in personeller:
                pid = p.get('PersonelTCKN')
                pname = p.get('PersonelName')
                psurname = p.get('PersonelSurname')
                ptitle = p.get('PersonelTitle')
                personel, _ = Personel.objects.get_or_create(
                    PersonelTCKN=pid,
                    defaults={'PersonelName': pname, 'PersonelSurname': psurname, 'PersonelTitle': ptitle}
                )
                # Eğer personel varsa, ad/ünvan güncelle
                if personel.PersonelName != pname or personel.PersonelSurname != psurname or personel.PersonelTitle != ptitle:
                    personel.PersonelName = pname
                    personel.PersonelSurname = psurname
                    personel.PersonelTitle = ptitle
                    personel.save()
                # Listeye ekle
                PersonelListesiKayit.objects.get_or_create(liste=liste, personel=personel)
                eklenenler.append(pid)
        return JsonResponse({'status': 'success', 'message': f'{len(eklenenler)} personel eklendi.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# Yeni Personel Ekleme İşlemi
def personel_ekle(request):
    if request.method == 'POST':
        # Form verilerini al
        personel_tc = request.POST['PersonelTCKN']
        personel_name = request.POST['PersonelName']
        personel_surname = request.POST['PersonelSurname']
        personel_title = request.POST['PersonelTitle']
        
        # Yeni personel kaydet
        personel = Personel(
            PersonelTCKN=personel_tc,
            PersonelName=personel_name,
            PersonelSurname=personel_surname,
            PersonelTitle=personel_title
        )
        personel.save()

        # Başarı mesajı ekleyebilirsiniz
        return redirect('mercis657:personeller')  # Personel listesine yönlendir
    return HttpResponse("Geçersiz istek", status=400)
def personel_update(request):
    if request.method == 'POST':
        personel_tc = request.POST.get('tckn')
        personel_name = request.POST.get('name')
        personel_surname = request.POST.get('surname')
        personel_title = request.POST.get('title')

        # Personeli bul
        personel = get_object_or_404(Personel, PersonelTCKN=personel_tc)
        
        # Güncellenen alanlar
        personel.PersonelName = personel_name
        personel.PersonelSurname = personel_surname
        personel.PersonelTitle = personel_title
        personel.save()  # Değişiklikleri kaydet
        
        return JsonResponse({'status': 'success'})  # Başarı mesajı

    return JsonResponse({'status': 'error'})  # Hatalı durum

```

---

### Dosya: views\personel_yonetim_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\personel_yonetim_views.py`

```python
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from ..models import Personel, PersonelListesiKayit


@login_required
def personel_yonetim(request):
    if not request.user.has_permission('ÇS 657 Personel Yönetimi'):
        return HttpResponseForbidden('Yetkiniz yok.')
    return render(request, 'mercis657/personel_yonetim.html')


@login_required
def personel_sorgula(request):
    if not request.user.has_permission('ÇS 657 Personel Yönetimi'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    ad_soyad = (request.GET.get('ad_soyad') or '').strip()
    tckn = (request.GET.get('tckn') or '').strip()
    donem = (request.GET.get('donem') or '').strip()  # YYYY/MM

    qs = Personel.objects.all().order_by('PersonelName', 'PersonelSurname')
    if ad_soyad:
        # Basit arama: hem ad hem soyad alanlarında küçük/büyük harfe duyarsız arama
        qs = qs.filter(PersonelName__icontains=ad_soyad) | qs.filter(PersonelSurname__icontains=ad_soyad)
    if tckn:
        qs = qs.filter(PersonelTCKN__icontains=tckn)

    results = []
    for p in qs:
        latest_kayit = PersonelListesiKayit.objects.filter(personel=p).order_by('-liste__yil', '-liste__ay').select_related('liste__birim').first()

        latest_info = None
        if latest_kayit:
            latest_info = {
                'yil': latest_kayit.liste.yil,
                'ay': latest_kayit.liste.ay,
                'birim': latest_kayit.liste.birim.BirimAdi,
                'birim_id': latest_kayit.liste.birim.BirimID,
            }

        # Dönem filtresi istendiyse, latest yerine o dönemdeki varlığı kontrol ederek filtreleyelim
        if donem:
            try:
                yil_str, ay_str = donem.split('/')
                yil, ay = int(yil_str), int(ay_str)
                donemde_var_mi = PersonelListesiKayit.objects.filter(personel=p, liste__yil=yil, liste__ay=ay).exists()
                if not donemde_var_mi:
                    continue
            except Exception:
                pass

        results.append({
            'id': p.PersonelID,
            'tckn': str(p.PersonelTCKN),
            'ad_soyad': f"{p.PersonelName} {p.PersonelSurname}",
            'unvan': p.PersonelTitle or '',
            'latest': latest_info,
        })

    return JsonResponse({'status': 'ok', 'data': results})


@login_required
def personel_listeleri(request, personel_id: int):
    if not request.user.has_permission('ÇS 657 Personel Yönetimi'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    personel = get_object_or_404(Personel, pk=personel_id)
    kayitlar = (
        PersonelListesiKayit.objects
        .filter(personel=personel)
        .select_related('liste__birim')
        .order_by('-liste__yil', '-liste__ay')
    )

    data = [
        {
            'yil': k.liste.yil,
            'ay': k.liste.ay,
            'birim': k.liste.birim.BirimAdi,
            'birim_id': k.liste.birim.BirimID,
        }
        for k in kayitlar
    ]

    return JsonResponse(data, safe=False)



```

---

### Dosya: views\raporlama_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\raporlama_views.py`

```python
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from PersonelYonSis.views import get_user_permissions
from ..models import Bildirim, Kurum, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin, UstBirim
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Prefetch
from decimal import Decimal
from mercis657.utils import hesapla_fazla_mesai
import os
import openpyxl
from io import BytesIO
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

def raporlama(request):
    bildirimler_by_birim = None
    donem = None
    kurum = None
    idare = None
    excel_url = None
    error_message = None
    info_message = None
    birimler_json = None
    birimler = Birim.objects.all()
    kurumlar = Kurum.objects.all()
    idareler = UstBirim.objects.all()

    # Form yerine GET parametrelerini doğrudan al
    donem_str = request.GET.get('donem')
    kurum = request.GET.get('kurum')
    idare = request.GET.get('idare')
    durum = request.GET.get('durum')  # "1", "0" veya ""

    toplam_kayit = 0

    # Dönem parametresi varsa veriyi çek
    if donem_str:
        try:
            # 'YYYY-MM' formatındaki stringi ayın ilk günü olan date objesine çevir
            donem = datetime.strptime(donem_str, "%Y-%m").date()

            bildirimler_query = Bildirim.objects.select_related(
                'Personel',
                'PersonelListesi__birim',
            ).filter(
                 DonemBaslangic=donem
            )

            if kurum:
                bildirimler_query = bildirimler_query.filter(
                    PersonelListesi__birim__Kurum__ad=kurum
                )
            if idare:
                bildirimler_query = bildirimler_query.filter(
                    PersonelListesi__birim__UstBirim__ad=idare
                )

            if durum == "1":
                bildirimler_query = bildirimler_query.filter(OnayDurumu=1)
            elif durum == "0":
                bildirimler_query = bildirimler_query.filter(OnayDurumu=0)

            # Bildirimleri çek ve PersonelListesi__birim'e göre grupla (Birim modelinde doğrudan bildirim_set yok)
            birim_ids_with_calisma = list(bildirimler_query.values_list('PersonelListesi__birim', flat=True).distinct())

            birimler_with_bildirimler = Birim.objects.filter(BirimID__in=birim_ids_with_calisma).order_by('BirimAdi')

            # Bildirimleri sıralı çek ve Python tarafında birim id'lerine göre grupla
            bildirimler_list = list(bildirimler_query.order_by('Personel__PersonelName').select_related('Personel', 'PersonelListesi'))
            bildirimler_map = {}
            for b in bildirimler_list:
                try:
                    birim_obj = getattr(b.PersonelListesi, 'birim', None)
                    birim_id = birim_obj.BirimID if birim_obj is not None else None
                except Exception:
                    birim_id = None
                if birim_id is None:
                    continue
                bildirimler_map.setdefault(birim_id, []).append(b)

            # Birimleri JSON'a çevir
            birimler_json = json.dumps([
                {'BirimID': b.BirimID, 'BirimAdi': b.BirimAdi} for b in birimler_with_bildirimler
            ])

            bildirimler_by_birim = []
            for birim in birimler_with_bildirimler:
                items = bildirimler_map.get(birim.BirimID, [])
                if items:
                    onaylanmis = sum(1 for c in items if c.OnayDurumu == 1)
                    beklemede = sum(1 for c in items if c.OnayDurumu == 0)
                    kilitli = sum(1 for c in items if c.MutemetKilit == True)
                    bildirimler_by_birim.append({
                        'birim': birim,
                        'bildirimler': items,
                        'personel_sayisi': len(set([getattr(c.Personel, 'PersonelID', None) for c in items])),
                        'onaylanmis_sayisi': onaylanmis,
                        'beklemede_sayisi': beklemede,
                        'kilitli_sayisi': kilitli,
                        })

            toplam_kayit = sum(len(birim['bildirimler']) for birim in bildirimler_by_birim)

            # Excel indirme linki oluştur
            if bildirimler_by_birim:
                 excel_url = reverse('mercis657:export_raporlama_excel')
                 excel_url += f'?donem={donem.strftime("%Y-%m")}'

                 if kurum:
                     excel_url += f'&kurum={kurum}'
                 if durum:
                     excel_url += f'&durum={durum}'
                 if idare:
                     excel_url += f'&idare={idare}'

            if toplam_kayit == 0:
                 info_message = "Seçilen dönem ve kuruma ait hizmet sunum çalışması bulunamadı."

        except ValueError:
             error_message = "Geçersiz dönem formatı seçildi."
        except Exception as e:
            # Hata yönetimi
            error_message = f"Rapor oluşturulurken bir hata oluştu: {str(e)}"
            print(f"Raporlama Hatası: {e}") # Konsola yazdır (geliştirme için)
    else:
        # İlk sayfa yüklemesi veya dönem seçilmemişse
        info_message = "Lütfen bir dönem ve isteğe bağlı kriterlerinizi seçerek raporlayın."

    kod_duzenleme_yetkisi = request.user.has_permission('ÇS 657 Birim Kodlarını Düzenleyebilir')
    bildirim_sayfasi_yetkisi = request.user.has_permission('ÇS 657 Bildirim İşlemleri')
    context = {
        # 'form': form, # Form kaldırıldı
        'bildirimler_by_birim': bildirimler_by_birim,
        'birimler': birimler, # Kurum seçimi için tüm birimleri geçiyoruz (kurum listesi çekmek için)
        'birimler_json': birimler_json,
        'kurumlar': kurumlar, # Kurum seçimi için tüm kurumları geçiyoruz
        'idareler': idareler,
        'selected_donem': donem_str, # Şablona dönemin string halini gönderelim ki selectbox'ta seçili kalsın
        'selected_kurum': kurum,
        'selected_idare': idare,
        'selected_durum': durum,
        'excel_url': excel_url,
        # 'is_form_valid': is_form_valid, # Form kaldırıldı
        'error_message': error_message,
        'info_message': info_message,
        'toplam_kayit': toplam_kayit,
        'kod_duzenleme_yetkisi': kod_duzenleme_yetkisi,
        'bildirim_sayfasi_yetkisi': bildirim_sayfasi_yetkisi,
    }
    return render(request, 'mercis657/raporlama.html', context)

def export_raporlama_excel(request):
    """
    Bildirimler bildirim koduna göre gruplandırılır ve her fazla mesai türü için ayrı satır oluşturulur.
    """
    donem_str = request.GET.get('donem')
    kurum = request.GET.get('kurum')
    idare = request.GET.get('idare')
    durum = request.GET.get('durum')

    if not donem_str:
        messages.error(request, "Lütfen bir dönem seçin.")
        return redirect('mercis657:raporlama')

    try:
        donem = datetime.strptime(donem_str, "%Y-%m").date()
    except ValueError:
        messages.error(request, "Geçersiz dönem formatı.")
        return redirect('mercis657:raporlama')

    # Fetch Bildirim queryset for the period
    bildirimler_qs = Bildirim.objects.select_related('Personel', 'PersonelListesi__birim').filter(DonemBaslangic=donem)
    if kurum:
        bildirimler_qs = bildirimler_qs.filter(PersonelListesi__birim__Kurum__ad=kurum)
    if idare:
        bildirimler_qs = bildirimler_qs.filter(PersonelListesi__birim__UstBirim__ad=idare)
    if durum == "1":
        bildirimler_qs = bildirimler_qs.filter(OnayDurumu=1)
    elif durum == "0":
        bildirimler_qs = bildirimler_qs.filter(OnayDurumu=0)

    if not bildirimler_qs.exists():
        messages.warning(request, "Seçilen filtreye uygun veri bulunamadı.")
        return redirect('mercis657:raporlama')

    # Şablon dosyasını yükle
    template_path = os.path.join(settings.STATIC_ROOT, 'excels', 'FazlaMesaiSablon.xlsx')
    if not os.path.exists(template_path):
        template_path = os.path.join(settings.BASE_DIR, 'static', 'excels', 'FazlaMesaiSablon.xlsx')
    
    try:
        workbook = openpyxl.load_workbook(template_path)
        worksheet = workbook.active
    except FileNotFoundError:
        messages.error(request, f"Şablon dosyası bulunamadı: {template_path}")
        return redirect('mercis657:raporlama')

    # Stil tanımlamaları
    from openpyxl.styles import Border, Side, PatternFill
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')

    current_row = 2  # Veri yazmaya 2. satırdan başla (başlık satırını atla)

    # Bildirimleri personel bazında grupla
    for bildirim in bildirimler_qs.order_by('PersonelListesi__birim__BirimAdi', 'Personel__PersonelName'):
        try:
            # Personel ve birim bilgilerini al
            personel = bildirim.Personel
            birim = bildirim.PersonelListesi.birim
            
            personel_tckn = getattr(personel, 'PersonelTCKN', '')
            personel_ad = getattr(personel, 'PersonelName', '')
            personel_soyisim = getattr(personel, 'PersonelSurname', '')
            birim_adi = getattr(birim, 'BirimAdi', '')
            kadro_durumu = getattr(personel, 'KadroDurumu', '')
            
            # Birim kodlarını al
            normal_nobet_kodu = getattr(birim, 'NormalNobetKodu', '1')
            bayram_nobet_kodu = getattr(birim, 'BayramNobetKodu', '')
            riskli_normal_nobet_kodu = getattr(birim, 'RiskliNormalNobetKodu', '')
            riskli_bayram_nobet_kodu = getattr(birim, 'RiskliBayramNobetKodu', '')
            
            # Gece birim kodlarını al
            normal_gece_nobet_kodu = getattr(birim, 'NormalGeceNobetKodu', '')
            bayram_gece_nobet_kodu = getattr(birim, 'BayramGeceNobetKodu', '')
            riskli_normal_gece_nobet_kodu = getattr(birim, 'RiskliNormalGeceNobetKodu', '')
            riskli_bayram_gece_nobet_kodu = getattr(birim, 'RiskliBayramGeceNobetKodu', '')
            
            # Her bir fazla mesai/icap türü için kontrol yap ve ayrı satır oluştur
            fazla_mesai_list = [
                ('NormalFazlaMesai', normal_nobet_kodu, bildirim.NormalFazlaMesai),
                ('BayramFazlaMesai', bayram_nobet_kodu, bildirim.BayramFazlaMesai),
                ('RiskliNormalFazlaMesai', riskli_normal_nobet_kodu, bildirim.RiskliNormalFazlaMesai),
                ('RiskliBayramFazlaMesai', riskli_bayram_nobet_kodu, bildirim.RiskliBayramFazlaMesai),
                # Gece
                ('GeceNormalFazlaMesai', normal_gece_nobet_kodu, bildirim.GeceNormalFazlaMesai),
                ('GeceBayramFazlaMesai', bayram_gece_nobet_kodu, bildirim.GeceBayramFazlaMesai),
                ('GeceRiskliNormalFazlaMesai', riskli_normal_gece_nobet_kodu, bildirim.GeceRiskliNormalFazlaMesai),
                ('GeceRiskliBayramFazlaMesai', riskli_bayram_gece_nobet_kodu, bildirim.GeceRiskliBayramFazlaMesai),
                # İcap
                ('NormalIcap', '17', bildirim.NormalIcap),
                ('BayramIcap', '18', bildirim.BayramIcap),
            ]

            for fm_type, birim_kodu, value in fazla_mesai_list:
                # Değerin boş veya 0'dan büyük olup olmadığını kontrol et
                try:
                    numeric_value = float(value) if value is not None else 0
                except (TypeError, ValueError):
                    numeric_value = 0
                
                # Sadece geçerli değerler ve 0'dan büyük değerler için satır oluştur
                if value is not None and value != '' and numeric_value > 0 and birim_kodu:
                    # Yeni satır için hücrelere verileri yaz
                    worksheet.cell(row=current_row, column=1, value=personel_tckn)
                    worksheet.cell(row=current_row, column=2, value=personel_ad)
                    worksheet.cell(row=current_row, column=3, value=personel_soyisim)
                    worksheet.cell(row=current_row, column=4, value=birim_kodu)  # İlgili birim kodunu 5. sütuna yaz
                    worksheet.cell(row=current_row, column=5, value=numeric_value)  # Değeri 6. sütuna yaz
                    worksheet.cell(row=current_row, column=7, value=birim_adi)  # Birim adını 7. sütuna yaz
                    worksheet.cell(row=current_row, column=8, value=fm_type)  # Fazla mesai türünü 8. sütuna yaz

                    # Sınır ve dolgu uygula
                    for col in range(1, 9):
                        worksheet.cell(row=current_row, column=col).border = thin_border
                        if kadro_durumu == "Geçici Gelen":
                            worksheet.cell(row=current_row, column=col).fill = green_fill

                    current_row += 1  # Bir sonraki satıra geç

        except Exception as e:
            print(f"Bildirim işlenirken hata: {e}")
            continue

    # Excel dosyasını kaydet
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name = f"FazlaMesaiBildirimleri_{donem_str}.xlsx"
    response['Content-Disposition'] = f'inline; filename="{file_name}"'
    return response


@require_POST
@login_required
def update_birim_kodlari_toplu(request):
    """Endpoint: Toplu birim kodlarını günceller.
    Beklenen payload: {'changes': [{'birim_id': id, 'NormalNobetKodu': val, 'BayramNobetKodu': val,...}, ...]}
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        changes = data.get('changes', [])
        
        if not changes:
            return JsonResponse({'status':'error','message':'Güncellenecek veri bulunamadı'}, status=400)

        # Permission check: kullanıcı birim bilgilerini düzenleyebilmeli
        if not request.user.has_permission('ÇS 657 Birim Kodlarını Düzenleyebilir'):
            return JsonResponse({'status':'error','message':'Yetkiniz yok'}, status=403)

        updated_count = 0
        errors = []
        
        with transaction.atomic():
            for change in changes:
                try:
                    birim_id = change.get('birim_id')
                    if not birim_id:
                        errors.append(f"Birim ID bulunamadı: {change}")
                        continue
                        
                    birim = Birim.objects.get(BirimID=birim_id)
                    
                    # Update allowed fields
                    for field in ['NormalNobetKodu','BayramNobetKodu','RiskliNormalNobetKodu','RiskliBayramNobetKodu','NormalGeceNobetKodu','BayramGeceNobetKodu','RiskliNormalGeceNobetKodu','RiskliBayramGeceNobetKodu']:
                        if field in change:
                            val = change[field]
                            setattr(birim, field, val)
                    
                    birim.save()
                    updated_count += 1
                    
                except Birim.DoesNotExist:
                    errors.append(f"Birim bulunamadı: {birim_id}")
                except Exception as e:
                    errors.append(f"Birim {birim_id} güncellenirken hata: {str(e)}")
        
        if errors:
            message = f"{updated_count} birim güncellendi. Hatalar: {'; '.join(errors)}"
            return JsonResponse({'status':'partial','message':message, 'errors':errors})
        else:
            return JsonResponse({'status':'success','message':f'{updated_count} birim başarıyla güncellendi'})
            
    except Exception as e:
        return JsonResponse({'status':'error','message':str(e)}, status=500)


@require_POST
@login_required
def kilit_tekil(request):
    """Endpoint: Verilen birim için seçilen dönemdeki Bildirimlerin MutemetKilit alanını toggle eder.
    Payload: {'birim_id': id, 'donem': 'YYYY-MM'}
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        birim_id = data.get('birim_id')
        donem_str = data.get('donem')
        donem = datetime.strptime(donem_str, "%Y-%m").date()

        bildirimler = Bildirim.objects.filter(PersonelListesi__birim__BirimID=birim_id, DonemBaslangic=donem)
        if not bildirimler.exists():
            return JsonResponse({'status':'error','message':'Bildirim bulunamadı'}, status=404)

        with transaction.atomic():
            for b in bildirimler:
                if b.MutemetKilit == True:
                    b.MutemetKilit = False
                    b.MutemetKilitUser = None
                    b.MutemetKilitTime = None
                else:
                    b.MutemetKilit = True
                    b.MutemetKilitUser = request.user
                    b.MutemetKilitTime = timezone.now()
                b.save()

        return JsonResponse({'status':'success','message':'Kilit durumu güncellendi'})
    except Exception as e:
        return JsonResponse({'status':'error','message':str(e)}, status=500)


@require_POST
@login_required
def kilit_toplu(request):
    """Endpoint: Tüm bildirimleri döneme göre kilitle veya aç.
    Payload: {'donem': 'YYYY-MM', 'action': 'lock'|'unlock'}
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        donem_str = data.get('donem')
        kurum = data.get('kurum')
        idare = data.get('idare')
        durum = data.get('durum')
        action = data.get('action')
        donem = datetime.strptime(donem_str, "%Y-%m").date()

        bildirimler = Bildirim.objects.filter(DonemBaslangic=donem)
        
        if kurum:
            bildirimler = bildirimler.filter(PersonelListesi__birim__Kurum__ad=kurum)
        if idare:
            bildirimler = bildirimler.filter(PersonelListesi__birim__UstBirim__ad=idare)
        
        # Durum kontrolü (hem string hem int gelebilir)
        if str(durum) == "1":
            bildirimler = bildirimler.filter(OnayDurumu=1)
        elif str(durum) == "0":
            bildirimler = bildirimler.filter(OnayDurumu=0)
        if not bildirimler.exists():
            return JsonResponse({'status':'error','message':'Bildirim bulunamadı'}, status=404)

        with transaction.atomic():
            for b in bildirimler:
                if action == 'unlock':
                    b.MutemetKilit = False
                    b.MutemetKilitUser = None
                    b.MutemetKilitTime = None
                else:
                    b.MutemetKilit = True
                    b.MutemetKilitUser = request.user
                    b.MutemetKilitTime = timezone.now()
                b.save()

        return JsonResponse({'status':'success','message':'Toplu işlem tamamlandı'})
    except Exception as e:
        return JsonResponse({'status':'error','message':str(e)}, status=500)

```

---

### Dosya: views\riskli_calisma_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\riskli_calisma_views.py`

```python
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ..models import Birim, PersonelListesi, Mesai, Bildirim
from ..utils import get_turkish_month_name, hesapla_riskli_calisma
import json
from datetime import date
import calendar

@login_required
def riskli_calisma_yonetim(request, birim_id):
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
         return HttpResponseForbidden("Yetkiniz yok.")
    
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
    except (ValueError, TypeError):
        today = date.today()
        year = today.year
        month = today.month

    birim = get_object_or_404(Birim, pk=birim_id)
    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
    
    donem_baslangic = date(year, month, 1)
    
    # Days info
    days_in_month = calendar.monthrange(year, month)[1]
    days = []
    for d in range(1, days_in_month + 1):
        dt = date(year, month, d)
        days.append({
            'day': d,
            'date_str': dt.strftime('%Y-%m-%d'),
            'is_weekend': dt.weekday() >= 5
        })
        
    personel_data = []
    if liste:
        kayitlar = liste.kayitlar.select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname')
        
        # Fetch Mesai records
        # Efficiently fetching all mesai for all personnel in the list for this month
        personel_ids = [k.personel.PersonelID for k in kayitlar]
        mesailer = Mesai.objects.filter(
            Personel__PersonelID__in=personel_ids,
            MesaiDate__year=year, 
            MesaiDate__month=month
        )

        mesai_map = {}
        for m in mesailer:
            pid = m.Personel_id
            d_str = m.MesaiDate.strftime('%Y-%m-%d')
            if pid not in mesai_map: mesai_map[pid] = {}
            mesai_map[pid][d_str] = m
            
        # Fetch existing Bildirim records for quick stat
        bildirimler = Bildirim.objects.filter(
            Personel__PersonelID__in=personel_ids,
            DonemBaslangic=donem_baslangic,
            SilindiMi=False
        )
        bildirim_map = {b.Personel_id: b for b in bildirimler}

        for kayit in kayitlar:
            p = kayit.personel
            p_mesailer = mesai_map.get(p.PersonelID, {})
            # Removed Bildirim based total riskli calculation logic
            
            # Recalculate Total Risk using utility function
            total_riskli = float(hesapla_riskli_calisma(kayit, year, month))
            
            day_status = {}
            for day_info in days:
                d_str = day_info['date_str']
                mesai = p_mesailer.get(d_str)
                risk_status = 'none'
                has_mesai = False
                mesai_id = None
                is_clickable = False
                
                if mesai:
                    has_mesai = True
                    mesai_id = mesai.MesaiID
                    risk_status = mesai.riskli_calisma or 'none'
                    
                    # Only clickable if MesaiTanim exists AND not Izin
                    if mesai.MesaiTanim and not mesai.Izin:
                        is_clickable = True
                
                day_status[d_str] = {
                    'has_mesai': has_mesai,
                    'risk_status': risk_status,
                    'mesai_id': mesai_id,
                    'is_clickable': is_clickable
                }

            personel_data.append({
                'id': p.PersonelID,
                'name': f"{p.PersonelName} {p.PersonelSurname}",
                'total_riskli': total_riskli,
                'days': day_status
            })

    context = {
        'birim': birim,
        'year': year,
        'month': month,
        'days': days,
        'personel_data': personel_data,
        'month_name': get_turkish_month_name(month)
    }
    return render(request, 'mercis657/riskli_calisma_yonetim.html', context)

@login_required
@require_POST
def riskli_calisma_kaydet(request):
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
         return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
         
    try:
        data = json.loads(request.body)
        updates = data.get('updates', []) 
        bulk_action = data.get('bulk_action') # 'all_full', 'all_clear' for specific filters
        
        # 'updates' contains individual cell changes: {mesai_id: X, status: Y}
        # or bulk changes can be handled by logic here.
        
        # 1. Process explicit updates
        for up in updates:
            mid = up.get('mesai_id')
            status = up.get('status') # 'none', 'full', 'nobet'
            
            if not mid: continue
            
            mesai = Mesai.objects.filter(MesaiID=mid).first()
            if mesai:
                if status == 'none':
                    mesai.riskli_calisma = None
                elif status in [Mesai.RISKLI_TAM, Mesai.RISKLI_NOBET]:
                    mesai.riskli_calisma = status
                mesai.save()
        
        # 2. Process bulk actions if provided
        if bulk_action:
             # Expects params to scope the bulk action
             target_type = data.get('target_type') # 'personel' or 'all'
             personel_id = data.get('personel_id')
             year = data.get('year')
             month = data.get('month')
             birim_id = data.get('birim_id')
             
             if not (year and month and birim_id):
                 return JsonResponse({'status': 'error', 'message': 'Eksik parametreler'}, status=400)
             
             # Safer query via PersonelListesi
             liste = PersonelListesi.objects.filter(birim_id=birim_id, yil=year, ay=month).first()
             if not liste:
                 return JsonResponse({'status': 'error', 'message': 'Liste bulunamadı'}, status=404)
                 
             personel_ids = liste.kayitlar.values_list('personel_id', flat=True)
             
             qs = Mesai.objects.filter(
                 MesaiDate__year=year,
                 MesaiDate__month=month,
                 Personel_id__in=personel_ids
             )
             
             if target_type == 'personel' and personel_id:
                 qs = qs.filter(Personel_id=personel_id)
             
             val = None
             if bulk_action == 'all_full': val = Mesai.RISKLI_TAM
             elif bulk_action == 'all_nobet': val = Mesai.RISKLI_NOBET
             elif bulk_action == 'all_clear': val = None
             
             if val is not None or bulk_action == 'all_clear':
                 qs.update(riskli_calisma=val)

        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

```

---

### Dosya: views\stop_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\stop_views.py`

```python
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from ..models import StopKaydi, Mesai
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
import datetime
from datetime import timedelta

@login_required
def stop_ekle(request, mesai_id):
    if not request.user.has_permission('ÇS 657 Stop Kaydı Ekleme'):
        messages.error(request, "Stop Kaydı Ekleme yetkiniz yok.")
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    mesai = get_object_or_404(Mesai, pk=mesai_id)
    # GET: render modal partial with existing stops (if any)
    if request.method == "GET":
        # ensure related person and mesai tanim prefetched
        mesai = Mesai.objects.select_related('Personel', 'MesaiTanim').prefetch_related('mercis657_stoplar').get(pk=mesai_id)
        return render(request, "mercis657/stop_modal.html", {"mesai": mesai})

    # POST: create a StopKaydi
    if request.method == "POST":
        baslangic_raw = request.POST.get("StopBaslangic")  # expected 'HH:MM' or 'HH:MM:SS'
        bitis_raw = request.POST.get("StopBitis")
        aciklama = request.POST.get("StopAciklama")
        if not baslangic_raw or not bitis_raw:
            return JsonResponse({'status': 'error', 'message': 'Zaman verisi eksik.'}, status=400)

        try:
            # parse time strings
            bas_time = datetime.time.fromisoformat(baslangic_raw)
            bit_time = datetime.time.fromisoformat(bitis_raw)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Zaman formatı okunamadı.'}, status=400)

        # combine with mesai date
        mesai_date = mesai.MesaiDate
        bas_dt = datetime.datetime.combine(mesai_date, bas_time)
        bit_dt = datetime.datetime.combine(mesai_date, bit_time)

        # If end is earlier or equal to start, assume next day
        if bit_dt <= bas_dt:
            bit_dt = bit_dt + timedelta(days=1)

        # make timezone-aware if naive
        if timezone.is_naive(bas_dt):
            bas_dt = timezone.make_aware(bas_dt, timezone.get_current_timezone())
        if timezone.is_naive(bit_dt):
            bit_dt = timezone.make_aware(bit_dt, timezone.get_current_timezone())

        stop = StopKaydi.objects.create(
            mesai=mesai,
            StopBaslangic=bas_dt,
            StopBitis=bit_dt,
            Aciklama=aciklama,
            created_by=request.user,
        )
        # return sure in hours
        return JsonResponse({"status": "success", "sure": stop.Sure})


@login_required
@require_POST
def stop_sil(request, stop_id):
    if not request.user.has_permission('ÇS 657 Stop Kaydı Ekleme'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    stop = get_object_or_404(StopKaydi, pk=stop_id)
    stop.delete()
    return JsonResponse({"status": "deleted"})

```

---

### Dosya: views\tanimlamalar_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\tanimlamalar_views.py`

```python
from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Bildirim, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin
from ..forms import ResmiTatilForm
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction

@login_required
@require_POST
def tatil_ekle(request):
    """ Yeni resmi tatil ekler """
    form = ResmiTatilForm(request.POST)
    
    if form.is_valid():
        # Aynı tarihe ait tatil kontrolü
        if ResmiTatil.objects.filter(TatilTarihi=form.cleaned_data['TatilTarihi']).exists():
            messages.error(request, "Bu tarihe ait bir resmi tatil zaten mevcut.")
            return redirect('mercis657:tanimlamalar')
        
        form.save()
        messages.success(request, "Resmi tatil başarıyla eklendi.")
    else:
        # Form hatalarını göster
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{form.fields[field].label}: {error}")
    
    return redirect('mercis657:tanimlamalar')

@login_required
@require_POST
def tatil_duzenle(request):
    """ Mevcut resmi tatili düzenler """
    tatil_id = request.POST.get('tatil_id')
    tatil = get_object_or_404(ResmiTatil, TatilID=tatil_id)
    
    form = ResmiTatilForm(request.POST, instance=tatil)
    
    if form.is_valid():
        # Aynı tarihe ait başka tatil kontrolü
        if ResmiTatil.objects.filter(TatilTarihi=form.cleaned_data['TatilTarihi']).exclude(TatilID=tatil_id).exists():
            messages.error(request, "Bu tarihe ait başka bir resmi tatil zaten mevcut.")
            return redirect('mercis657:tanimlamalar')
        
        form.save()
        messages.success(request, "Resmi tatil başarıyla güncellendi.")
    else:
        # Form hatalarını göster
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{form.fields[field].label}: {error}")
    
    return redirect('mercis657:tanimlamalar')

@login_required
@require_POST
def tatil_sil(request, tatil_id):
    """ Resmi tatili siler """
    tatil = get_object_or_404(ResmiTatil, TatilID=tatil_id)
    tatil.delete()
    messages.success(request, "Resmi tatil başarıyla silindi.")
    return redirect('mercis657:tanimlamalar')

```

---

### Dosya: views\vardiya_dagilim_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\vardiya_dagilim_views.py`

```python
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template.loader import render_to_string
from ..models import Kurum, UstBirim, Idareci, Bina, Mesai, MesaiKontrol, PersonelListesiKayit
import json
from datetime import datetime
import pdfkit

@login_required
def vardiya_dagilim(request):
    """
    Vardiya dağılımı ana sayfası.
    Filtreleme seçeneklerini (select listeleri) context olarak gönderir.
    """
    context = {
        'kurumlar': Kurum.objects.filter(aktif=True),
        'ust_birimler': UstBirim.objects.filter(aktif=True),
        'idareciler': Idareci.objects.filter(aktif=True),
        'binalar': Bina.objects.filter(aktif=True),
        'bugun': datetime.now().strftime('%Y-%m-%d'),
    }
    return render(request, 'mercis657/vardiya_dagilim.html', context)

@login_required
@require_POST
def vardiya_dagilim_search(request):
    """
    AJAX endpoint: Filtrelere göre Mesai kayıtlarını sorgular.
    JSON input: {kurum_id, ust_birim_id, idareci_id, bina_id, tarih, vardiya}
    Response: {results: [{bina, birim, personeller: [...]}, ...]}
    """
    try:
        data = json.loads(request.body)
        kurum_id = data.get('kurum_id')
        ust_birim_id = data.get('ust_birim_id')
        idareci_id = data.get('idareci_id')
        bina_id = data.get('bina_id')
        tarih1 = data.get('tarih1')
        tarih2 = data.get('tarih2')
        vardiya_tipi = data.get('vardiya')  # 'gunduz', 'aksam', 'gece', 'tumu'
        mesai_notu = data.get('mesai_notu', [])

        if not tarih1 or not tarih2:
            return JsonResponse({'status': 'error', 'message': 'Tarih aralığı eksik'}, status=400)

        # Temel sorgu: Tarih aralığı ve geçerli mesai tanımı
        mesai_qs = Mesai.objects.filter(
            MesaiDate__range=[tarih1, tarih2],
            MesaiTanim__isnull=False,
            Izin__isnull=True  # İzinli olanlar hariç
        ).select_related(
            'Personel', 
            'MesaiTanim'
        ).prefetch_related('mesai_kontrolleri')

        # Vardiya tipi filtresi
        if vardiya_tipi == 'gunduz':
            mesai_qs = mesai_qs.filter(MesaiTanim__GunduzMesaisi=True)
        elif vardiya_tipi == 'aksam':
            mesai_qs = mesai_qs.filter(MesaiTanim__AksamMesaisi=True)
        elif vardiya_tipi == 'gece':
            mesai_qs = mesai_qs.filter(MesaiTanim__GeceMesaisi=True)

        if mesai_notu and len(mesai_notu) > 0:
            mesai_qs = mesai_qs.filter(MesaiNotu__in=mesai_notu)

        # PersonelListesiKayit üzerinden birim/bina filtreleme
        yil1, ay1 = int(tarih1.split('-')[0]), int(tarih1.split('-')[1])
        yil2, ay2 = int(tarih2.split('-')[0]), int(tarih2.split('-')[1])
        
        kayit_qs = PersonelListesiKayit.objects.filter(
            Q(liste__yil=yil1, liste__ay=ay1) | Q(liste__yil=yil2, liste__ay=ay2)
        ).select_related('liste__birim', 'liste__birim__Bina', 'personel')

        if kurum_id:
            kayit_qs = kayit_qs.filter(liste__birim__Kurum_id=kurum_id)
        if ust_birim_id:
            kayit_qs = kayit_qs.filter(liste__birim__UstBirim_id=ust_birim_id)
        if idareci_id:
            kayit_qs = kayit_qs.filter(liste__birim__Idareci_id=idareci_id)
        if bina_id:
            kayit_qs = kayit_qs.filter(liste__birim__Bina_id=bina_id)

        # Filtrelenen personellerin ID listesi
        personel_ids = kayit_qs.values_list('personel_id', flat=True)
        
        # Mesai sorgusunu bu personellerle sınırla
        mesai_qs = mesai_qs.filter(Personel_id__in=personel_ids)

        # Sonuçları grupla: Bina -> Birim -> Personel Listesi
        # Veriyi işlemek için dictionary kullanalım
        grouped_data = {}
        
        # PersonelListesiKayit verilerini memory'e alalım (personel_id -> birim bilgisi)
        personel_birim_map = {}
        for kayit in kayit_qs:
            birim = kayit.liste.birim
            bina_ad = birim.Bina.ad if birim.Bina else "Diğer"
            personel_birim_map[kayit.personel_id] = {
                'bina': bina_ad,
                'birim': birim.BirimAdi,
                'unvan': kayit.personel.PersonelTitle or ""
            }

        results = []
        
        for mesai in mesai_qs:
            p_info = personel_birim_map.get(mesai.Personel_id)
            if not p_info:
                continue # Listede olmayan ama mesaisi olan (eski kayıt vs) atla

            bina = p_info['bina']
            birim = p_info['birim']
            
            if bina not in grouped_data:
                grouped_data[bina] = {}
            if birim not in grouped_data[bina]:
                grouped_data[bina][birim] = []

            # Kontrol durumu
            kontrol_kaydi = mesai.mesai_kontrolleri.first()
            kontrol_durumu = kontrol_kaydi.kontrol if kontrol_kaydi else None

            grouped_data[bina][birim].append({
                'mesai_id': mesai.MesaiID,
                'personel_ad': f"{mesai.Personel.PersonelName} {mesai.Personel.PersonelSurname}",
                'unvan': p_info['unvan'],
                'mesai_tarih': mesai.MesaiDate.strftime('%d.%m.%Y'),
                'mesai_saat': mesai.MesaiTanim.Saat,
                'mesai_notu': mesai.MesaiNotu,
                'kontrol': kontrol_durumu
            })

        # Frontend formatına dönüştür
        sorted_binas = sorted(grouped_data.keys())
        final_results = []
        
        for bina in sorted_binas:
            birimler = grouped_data[bina]
            sorted_birims = sorted(birimler.keys())
            birim_list = []
            for birim_adi in sorted_birims:
                birim_list.append({
                    'ad': birim_adi,
                    'personeller': birimler[birim_adi]
                })
            final_results.append({
                'bina': bina,
                'birimler': birim_list
            })

        return JsonResponse({'status': 'success', 'results': final_results})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def vardiya_dagilim_kaydet(request):
    """
    AJAX endpoint: Gönderilen kontrol verilerini kaydeder.
    JSON input: [{mesai_id: 1, kontrol: true/false}, ...]
    """
    if not request.user.has_permission('ÇS 657 Vardiya Dağılımı Kontrolü'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok'}, status=403)
    try:
        data = json.loads(request.body)
        updates = data.get('updates', [])
        
        for item in updates:
            mesai_id = item.get('mesai_id')
            kontrol_val = item.get('kontrol')
            
            if mesai_id is not None and kontrol_val is not None:
                MesaiKontrol.objects.update_or_create(
                    mesai_id=mesai_id,
                    defaults={
                        'kontrol': kontrol_val,
                        'kontrol_yapan': request.user,
                        'kontrol_tarihi': datetime.now()
                    }
                )
                
        return JsonResponse({'status': 'success', 'message': 'Kayıtlar güncellendi.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def vardiya_dagilim_pdf(request):
    """
    Seçili filtrelerle PDF rapor oluşturur.
    GET params: kurum_id, ust_birim_id, idareci_id, bina_id, tarih, vardiya
    """
    try:
        kurum_id = request.GET.get('kurum_id')
        ust_birim_id = request.GET.get('ust_birim_id')
        idareci_id = request.GET.get('idareci_id')
        bina_id = request.GET.get('bina_id')
        tarih1 = request.GET.get('tarih1')
        tarih2 = request.GET.get('tarih2')
        vardiya_tipi = request.GET.get('vardiya')
        mesai_notu = request.GET.getlist('mesai_notu')
        
        if not tarih1 or not tarih2:
            bugun = datetime.now().strftime('%Y-%m-%d')
            tarih1 = bugun
            tarih2 = bugun

        # --- Filtreleme Mantığı (Search ile aynı) ---
        mesai_qs = Mesai.objects.filter(
            MesaiDate__range=[tarih1, tarih2],
            MesaiTanim__isnull=False,
            Izin__isnull=True
        ).select_related(
            'Personel', 
            'MesaiTanim'
        ).prefetch_related('mesai_kontrolleri')

        if vardiya_tipi == 'gunduz':
            mesai_qs = mesai_qs.filter(MesaiTanim__GunduzMesaisi=True)
        elif vardiya_tipi == 'aksam':
            mesai_qs = mesai_qs.filter(MesaiTanim__AksamMesaisi=True)
        elif vardiya_tipi == 'gece':
            mesai_qs = mesai_qs.filter(MesaiTanim__GeceMesaisi=True)

        if mesai_notu and len(mesai_notu) > 0:
            mesai_qs = mesai_qs.filter(MesaiNotu__in=mesai_notu)

        yil1, ay1 = int(tarih1.split('-')[0]), int(tarih1.split('-')[1])
        yil2, ay2 = int(tarih2.split('-')[0]), int(tarih2.split('-')[1])
        
        kayit_qs = PersonelListesiKayit.objects.filter(
            Q(liste__yil=yil1, liste__ay=ay1) | Q(liste__yil=yil2, liste__ay=ay2)
        ).select_related('liste__birim', 'liste__birim__Bina', 'personel')

        if kurum_id:
            kayit_qs = kayit_qs.filter(liste__birim__Kurum_id=kurum_id)
        if ust_birim_id:
            kayit_qs = kayit_qs.filter(liste__birim__UstBirim_id=ust_birim_id)
        if idareci_id:
            kayit_qs = kayit_qs.filter(liste__birim__Idareci_id=idareci_id)
        if bina_id:
            kayit_qs = kayit_qs.filter(liste__birim__Bina_id=bina_id)

        personel_ids = kayit_qs.values_list('personel_id', flat=True)
        mesai_qs = mesai_qs.filter(Personel_id__in=personel_ids)

        grouped_data = {}
        personel_birim_map = {}
        for kayit in kayit_qs:
            birim = kayit.liste.birim
            bina_ad = birim.Bina.ad if birim.Bina else "Diğer"
            personel_birim_map[kayit.personel_id] = {
                'bina': bina_ad,
                'birim': birim.BirimAdi,
                'unvan': kayit.personel.PersonelTitle or ""
            }

        for mesai in mesai_qs:
            p_info = personel_birim_map.get(mesai.Personel_id)
            if not p_info:
                continue 

            bina = p_info['bina']
            birim = p_info['birim']
            
            if bina not in grouped_data:
                grouped_data[bina] = {}
            if birim not in grouped_data[bina]:
                grouped_data[bina][birim] = []

            kontrol_kaydi = mesai.mesai_kontrolleri.first()
            kontrol_durumu = kontrol_kaydi.kontrol if kontrol_kaydi else None

            grouped_data[bina][birim].append({
                'mesai_id': mesai.MesaiID,
                'personel_ad': f"{mesai.Personel.PersonelName} {mesai.Personel.PersonelSurname}",
                'unvan': p_info['unvan'],
                'mesai_tarih': mesai.MesaiDate.strftime('%d.%m.%Y'),
                'mesai_saat': mesai.MesaiTanim.Saat,
                'kontrol': kontrol_durumu
            })

        sorted_binas = sorted(grouped_data.keys())
        final_results = []
        for bina in sorted_binas:
            birimler = grouped_data[bina]
            sorted_birims = sorted(birimler.keys())
            birim_list = []
            for birim_adi in sorted_birims:
                birim_list.append({
                    'ad': birim_adi,
                    'personeller': birimler[birim_adi]
                })
            final_results.append({
                'bina': bina,
                'birimler': birim_list
            })
        
        # --- PDF Oluşturma ---
        context = {
            'results': final_results,
            'tarih1': tarih1,
            'tarih2': tarih2,
            'vardiya': vardiya_tipi
        }
        html_string = render_to_string('mercis657/pdf/vardiya_dagilim_pdf.html', context)
        
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'footer-center': '[page] / [topage]',
            'footer-font-size': '10',
            'margin-bottom': '15mm',
            'margin-top': '15mm',
            'orientation': 'Portrait'
        }

        pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="vardiya_dagilim_{tarih1}_{tarih2}.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Hata oluştu: {str(e)}")

```

---

### Dosya: views\yonetici_views.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\yonetici_views.py`

```python
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required

from ..models import Birim, PersonelListesi, PersonelListesiKayit, Kurum, UstBirim, Idareci, IlkListe


@login_required
def birim_listeleri(request):
    # 🔹 Dönem parametresi (YYYY/MM)
    selected_donem = request.GET.get("donem", "")
    selected_birim_adi = request.GET.get("birim_adi", "").strip()
    selected_kurum = request.GET.get("kurum", "")
    selected_ust_birim = request.GET.get("ust_birim", "")
    selected_idareci = request.GET.get("idareci", "")

    # 🔹 Dönem listesi: -6 ay ile +2 ay
    today = date.today().replace(day=1)
    donemler = []
    for i in range(-6, 3):
        d = today + relativedelta(months=i)
        value = f"{d.year}/{d.month:02d}"
        label = value
        donemler.append({"value": value, "label": label})

    # 🔹 Sorgu
    queryset = Birim.objects.select_related("Kurum", "UstBirim", "Idareci")

    if selected_birim_adi:
        queryset = queryset.filter(BirimAdi__icontains=selected_birim_adi)
    if selected_kurum:
        queryset = queryset.filter(Kurum_id=selected_kurum)
    if selected_ust_birim:
        queryset = queryset.filter(UstBirim_id=selected_ust_birim)
    if selected_idareci:
        queryset = queryset.filter(Idareci_id=selected_idareci)

    # 🔹 Seçili döneme göre PersonelListesi eşleştir
    yil, ay = None, None
    if selected_donem:
        try:
            yil, ay = map(int, selected_donem.split("/"))
        except:
            yil, ay = None, None

    birimler_data = []
    for idx, birim in enumerate(queryset, start=1):
        liste = None
        personel_sayisi = 0
        created_by = None
        if yil and ay:
            liste = PersonelListesi.objects.filter(birim=birim, yil=yil, ay=ay).first()
            if liste:
                personel_sayisi = PersonelListesiKayit.objects.filter(liste=liste).count()
                created_by = liste.created_by

        birimler_data.append({
            "sira": idx,
            "birim": birim,
            "liste": liste,
            "personel_sayisi": personel_sayisi,
            "created_by": created_by,
            "ilk_liste": IlkListe.objects.filter(PersonelListesi=liste).first() if liste else None,
        })

    context = {
        "donemler": donemler,
        "selected_donem": selected_donem,
        "birimler_data": birimler_data,
        "kurumlar": Kurum.objects.all(),
        "ust_birimler": UstBirim.objects.all(),
        "idareciler": Idareci.objects.all(),
        "selected_kurum": selected_kurum,
        "selected_ust_birim": selected_ust_birim,
        "selected_idareci": selected_idareci,
        "selected_birim_adi": selected_birim_adi,
    }
    return render(request, "mercis657/birim_listeleri.html", context)

```

---

### Dosya: views\__init__.py
Path: `d:/Github/PerYonSis/PersonelYonSis/mercis657\views\__init__.py`

```python
from .main_views import *
from .vardiya_dagilim_views import *
from .cizelge_edit_views import *
from .birim_views import *
from .personel_views import *
from .izin_views import *
from .mesai_views import *
from .mazeret_views import *
from .personel_islem_views import *
from .bildirim_views import *
from .tanimlamalar_views import *
from .raporlama_views import *
from .yonetici_views import *
from .stop_views import *
from .ilk_liste_views import *
from .imza_cizelgeleri_views import *
from .gunluk_izin_takibi_views import *
```

---

