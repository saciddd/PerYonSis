from PersonelYonSis.FMConnection.KDHIzin import sync_personel_to_filemaker
from django.db import models
from datetime import date

from ik_core.models.BirimYonetimi import PersonelBirim

from .valuelists import (
    TESKILAT_DEGERLERI, 
    EGITIM_DEGERLERI, 
    ENGEL_DERECESI_DEGERLERI, 
    MAZERET_DEGERLERI, 
    OZEL_DURUM_DEGERLERI, 
    AYRILMA_NEDENI_DEGERLERI
)

class Kurum(models.Model):
    ad = models.CharField(max_length=150)
    def __str__(self):
        return self.ad
    # ...other fields...

class Unvan(models.Model):
    ad = models.CharField(max_length=100)
    sinif = models.CharField(max_length=50)
    def __str__(self):
        return self.ad
    # ...other fields...

class Brans(models.Model):
    ad = models.CharField(max_length=100)
    unvan = models.ForeignKey(Unvan, on_delete=models.CASCADE)
    def __str__(self):
        return self.ad
    # ...other fields...

class OzelDurum(models.Model):
    kod = models.CharField(max_length=30, unique=True)
    ad = models.CharField(max_length=100)

    def __str__(self):
        return self.ad

class KisaUnvan(models.Model):
    ad = models.CharField(max_length=100, unique=True, verbose_name="Kısa Ünvan / Grup")
    ust_birim = models.ForeignKey('ik_core.UstBirim', on_delete=models.SET_NULL, null=True, verbose_name="Bağlı Olduğu Üst Birim", blank=True)

    @property
    def isci_unvani(self):
        # İlişkili tüm unvanları kontrol et
        # Reverse relation default name: unvanbranseslestirme_set
        for eslesme in self.unvanbranseslestirme_set.all():
            unvan_ad = eslesme.unvan.ad
            if unvan_ad:
                # Türkçe karakter duyarlı küçük harfe çevirme
                unvan_ad_lower = unvan_ad.replace('İ', 'i').replace('I', 'ı').lower()
                if "işçi" in unvan_ad_lower:
                    return True
        return False
    
    def __str__(self):
        if self.ust_birim:
             return f"{self.ad} - {self.ust_birim.ad}"
        return self.ad

    class Meta:
        verbose_name = "Kısa Ünvan"
        verbose_name_plural = "Kısa Ünvanlar"

class UnvanBransEslestirme(models.Model):
    unvan = models.ForeignKey(Unvan, on_delete=models.CASCADE)
    brans = models.ForeignKey(Brans, on_delete=models.SET_NULL, null=True, blank=True)
    kisa_unvan = models.ForeignKey(KisaUnvan, on_delete=models.CASCADE, verbose_name="Kısa Ünvan")

    def __str__(self):
        if self.brans:
            return f"{self.unvan.ad} - {self.brans.ad}"
        return self.unvan.ad

    class Meta:
        unique_together = ('unvan', 'brans')
        verbose_name = "Ünvan Branş Eşleştirme"
        verbose_name_plural = "Ünvan Branş Eşleştirmeleri"

class Personel(models.Model):
    # Kişi bilgileri
    tc_kimlik_no = models.CharField(max_length=11, unique=True)
    ad = models.CharField(max_length=50)
    soyad = models.CharField(max_length=50)
    unvan = models.ForeignKey(Unvan, on_delete=models.SET_NULL, null=True)
    brans = models.ForeignKey(Brans, on_delete=models.SET_NULL, null=True)
    unvan_brans_eslestirme = models.ForeignKey(UnvanBransEslestirme, on_delete=models.SET_NULL, null=True, verbose_name="Ünvan Branş Eşleştirme", blank=True)
    sicil_no = models.CharField(max_length=30, blank=True, null=True)
    dogum_tarihi = models.DateField(null=True, blank=True)
    cinsiyet = models.CharField(max_length=6, choices=[('Erkek', 'Erkek'), ('Kadin', 'Kadın')], blank=True, null=True)
    # Kurumsal bilgiler
    kurum = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, related_name='kurum_personelleri')
    kadro_yeri = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, related_name='kadro_personelleri')
    fiili_gorev_yeri = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, related_name='fiili_gorev_personelleri')
    kadrolu_personel = models.BooleanField(default=True, null=True, blank=True)
    # Görev bilgileri
    atama_karar_tarihi = models.DateField(null=True, blank=True)
    atama_karar_no = models.CharField(max_length=50, blank=True, null=True)
    goreve_baslama_tarihi = models.DateField(null=True, blank=True)
    memuriyete_baslama_tarihi = models.DateField(null=True, blank=True)
    kamu_baslangic_tarihi = models.DateField(null=True, blank=True)
    teskilat = models.CharField(max_length=50, choices=TESKILAT_DEGERLERI, blank=True, null=True)
    emekli_sicil_no = models.CharField(max_length=30, blank=True, null=True)
    tahsil_durumu = models.CharField(max_length=30, choices=EGITIM_DEGERLERI, blank=True, null=True)
    aile_hek_sozlesmesi = models.BooleanField(default=False, null=True, blank=True)
    aday_memur = models.BooleanField(default=False, null=True, blank=True)
    # Mazeret bilgileri
    mazeret_durumu = models.CharField(max_length=30, choices=MAZERET_DEGERLERI, blank=True, null=True)
    mazeret_baslangic = models.DateField(null=True, blank=True)
    mazeret_bitis = models.DateField(null=True, blank=True)
    # Özel durum bilgileri
    ozel_durumu = models.ManyToManyField(
        'OzelDurum',
        blank=True,
        related_name='personeller'
    )
    ozel_durumu_aciklama = models.TextField(blank=True, null=True)
    engel_orani = models.TextField(null=True, blank=True)
    vergi_indirimi = models.CharField(max_length=31, choices=ENGEL_DERECESI_DEGERLERI, blank=True, null=True)
    # İzin bilgileri
    memur_devreden_izin = models.FloatField(default=0, null=True, blank=True)
    memur_hak_ettigi_izin = models.FloatField(default=0, null=True, blank=True)
    # kalan_izin hesaplanacak, şimdilik yorum
    # İletişim bilgileri
    adres = models.TextField(blank=True, null=True)
    telefon = models.CharField(max_length=14, blank=True, null=True)
    eposta = models.EmailField(blank=True, null=True)
    # Ayrılış bilgileri
    ayrilma_tarihi = models.DateField(null=True, blank=True)
    ayrilma_nedeni = models.CharField(max_length=30, choices=AYRILMA_NEDENI_DEGERLERI, blank=True, null=True)
    ayrilma_detay = models.TextField(blank=True, null=True)
    # Diğer bilgiler
    dhy = models.BooleanField(default=False)
    sgk = models.BooleanField(default=False)
    dss = models.BooleanField(default=False)
    shcek = models.BooleanField(default=False)

    # Kayıt tarihi
    kayit_tarihi = models.DateField(auto_now_add=True)

    @property
    def ad_soyad(self):
        return f"{self.ad} {self.soyad}".strip()

    @property
    def yas(self):
        if self.dogum_tarihi:
            today = date.today()
            return today.year - self.dogum_tarihi.year - ((today.month, today.day) < (self.dogum_tarihi.month, self.dogum_tarihi.day))
        return None

    @property
    def kisa_unvan(self):
        # unvan_brans_eslestirme tablosunda personelin unvan ve brans değerleriyle eşleşen kisa_unvan değerini döndürür
        eslesme = UnvanBransEslestirme.objects.filter(unvan=self.unvan, brans=self.brans).first()
        if eslesme:
            return eslesme.kisa_unvan.ad
        return None

    @property
    def burc(self):
        if not self.dogum_tarihi:
            return None
        # 'burc' template filter yoksa, string döndür
        from .valuelists import get_burc_for_date
        return get_burc_for_date(self.dogum_tarihi)

    @property
    def memuriyet_durumu(self):
        if self.teskilat == "İşçi Personel 696 (Döner Sermaye)":
            return "SÜREKLİ İŞÇİ (696)"
        elif self.teskilat == "İşçi Personel (Genel Bütçe)":
            return "İşçi Personel"
        else:
            return "Memur (657)"

    @property
    def kadro_durumu(self):
        if self.kadrolu_personel:
            return "Kadrolu"
        else:
            return "Geçici Gelen"

    @property
    def durum(self):
        today = date.today()
        if self.kadrolu_personel:
            if self.ayrilma_tarihi and self.ayrilma_tarihi <= today:
                return "Kurumdan Ayrıldı"
            # Check for active temporary assignments (bitis is null or in the future)
            active_gorev = self.gecicigorev_set.filter(
                models.Q(gecici_gorev_bitis__isnull=True) | models.Q(gecici_gorev_bitis__gte=today),
                gecici_gorev_baslangic__lte=today
            ).exists()
            if active_gorev:
                return "Pasif" # More descriptive status
            return "Aktif"
        else:
            # For non-kadrolu, maybe active means they have an ongoing assignment?
            # Assuming similar logic: active if currently on an assignment.
            active_gorev = self.gecicigorev_set.filter(
                models.Q(gecici_gorev_bitis__isnull=True) | models.Q(gecici_gorev_bitis__gte=today),
                gecici_gorev_baslangic__lte=today
            ).exists()
            return "Aktif" if active_gorev else "Asıl Kurumuna Döndü" # Or adjust as needed

    @property
    def memuriyet_durumu(self):
        if self.teskilat == "İşçi Personel 696 (Döner Sermaye)":
            return "Sürekli İşçi (696)"
        elif self.teskilat == "İşçi Personel (Genel Bütçe)":
            return "İşçi Personel"
        else:
            return "Memur (657)"

    @property
    def sinif(self):
        return self.unvan.sinif if self.unvan else ""

    @property
    def aktif_sendika(self):
        """
        Personelin en son GİRİŞ hareketi olan sendikasını döndürür.
        Çıkıştan sonra tekrar giriş varsa onu dikkate alır.
        """
        # Son GİRİŞ hareketini bul
        son_giris = self.sendika_hareketleri.filter(hareket_tipi='GIRIS').order_by('-hareket_tarihi', '-uyelik_id').first()
        if not son_giris:
            return None
        # Son GİRİŞ'ten sonra bir ÇIKIŞ var mı?
        cikis_sonra = self.sendika_hareketleri.filter(
            hareket_tipi='CIKIS',
            hareket_tarihi__gte=son_giris.hareket_tarihi
        ).order_by('hareket_tarihi', 'uyelik_id').first()
        if cikis_sonra:
            return None
        return son_giris.sendika
    # Kalan izin hesaplaması için not:
    # @property
    # def kalan_izin(self):
    #     if self.memuriyet_durumu == "Memur (657)":
    #         return self.memur_devreden_izin + self.memur_hak_ettigi_izin - ... # mevcut yıl kullandığı izinler
    #     else:
    #         return ... # YillikIzinHakedis modeline göre hesaplanacak

    # Personelin en son çalıştığı birim bilgisini al
    @property
    def son_birim_kaydi(self):

        latest_kayit = PersonelBirim.objects.filter(personel=self).order_by('-gecis_tarihi').select_related('birim').first()
        if latest_kayit:
            return latest_kayit.birim.ad
        return None

    @property
    def son_mercis657_listesi(self):
        try:
            from mercis657.models import PersonelListesiKayit, Personel as MercisPersonel
            
            # TCKN ile mercis657 personelini bul
            if not self.tc_kimlik_no:
                return None

            mercis_personel = MercisPersonel.objects.filter(PersonelTCKN=self.tc_kimlik_no).first()
            if not mercis_personel:
                return None
                
            latest_kayit = PersonelListesiKayit.objects.filter(personel=mercis_personel).order_by('-liste__yil', '-liste__ay').select_related('liste__birim').first()

            if latest_kayit:
                return {
                    'yil': latest_kayit.liste.yil,
                    'ay': latest_kayit.liste.ay,
                    'birim': latest_kayit.liste.birim.BirimAdi,
                    'birim_id': latest_kayit.liste.birim.BirimID,
                }
            return None
        except Exception as e:
            return None

    @property
    def son_hizmet_sunum_bildirimi(self):
        try:
            from hizmet_sunum_app.models import HizmetSunumCalismasi, Personel as HizmetPersonel
            
            # TCKN ile hizmet sunum personelini bul
            if not self.tc_kimlik_no:
                return None

            hizmet_personel = HizmetPersonel.objects.filter(TCKimlikNo=self.tc_kimlik_no).first()
            if not hizmet_personel:
                return None
                
            latest_calisma = HizmetSunumCalismasi.objects.filter(PersonelId=hizmet_personel).order_by('-Donem').select_related('CalisilanBirimId').first()

            if latest_calisma:
                return {
                    'yil': latest_calisma.Donem.year,
                    'ay': latest_calisma.Donem.month,
                    'birim': latest_calisma.CalisilanBirimId.BirimAdi,
                    'birim_id': latest_calisma.CalisilanBirimId.BirimId,
                }
            return None
        except Exception as e:
            return None

    def __str__(self):
        return self.ad_soyad
    
    def save(self, *args, **kwargs):
        """Kaydı kaydet ve FileMaker senkronizasyonu tetikle"""
        super().save(*args, **kwargs)
        try:
            sync_personel_to_filemaker(self)
        except Exception as e:
            print(f"[FM SYNC HATA] {self.tc_kimlik_no}: {e}")
