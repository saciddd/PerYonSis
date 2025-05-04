from django.db import models
from datetime import date
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

class Personel(models.Model):
    # Kişi bilgileri
    tc_kimlik_no = models.CharField(max_length=11, unique=True)
    ad = models.CharField(max_length=50)
    soyad = models.CharField(max_length=50)
    unvan = models.ForeignKey(Unvan, on_delete=models.SET_NULL, null=True)
    brans = models.ForeignKey(Brans, on_delete=models.SET_NULL, null=True)
    sicil_no = models.CharField(max_length=30, blank=True)
    dogum_tarihi = models.DateField(null=True, blank=True)
    cinsiyet = models.CharField(max_length=6, choices=[('Erkek', 'Erkek'), ('Kadin', 'Kadın')])
    # Kurumsal bilgiler
    kurum = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, related_name='kurum_personelleri')
    kadro_yeri = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, related_name='kadro_personelleri')
    fiili_gorev_yeri = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, related_name='fiili_gorev_personelleri')
    kadrolu_personel = models.BooleanField(default=True)
    # Görev bilgileri
    atama_karar_tarihi = models.DateField(null=True, blank=True)
    atama_karar_no = models.CharField(max_length=50, blank=True)
    goreve_baslama_tarihi = models.DateField(null=True, blank=True)
    memuriyete_baslama_tarihi = models.DateField(null=True, blank=True)
    kamu_baslangic_tarihi = models.DateField(null=True, blank=True)
    teskilat = models.CharField(max_length=50, choices=TESKILAT_DEGERLERI)
    emekli_sicil_no = models.CharField(max_length=30, blank=True)
    tahsil_durumu = models.CharField(max_length=30, choices=EGITIM_DEGERLERI)
    aile_hek_sozlesmesi = models.BooleanField(default=False)
    # Mazeret bilgileri
    mazeret_durumu = models.CharField(max_length=30, choices=MAZERET_DEGERLERI, blank=True)
    mazeret_baslangic = models.DateField(null=True, blank=True)
    mazeret_bitis = models.DateField(null=True, blank=True)
    # Özel durum bilgileri
    ozel_durumu = models.ManyToManyField(
        'OzelDurum',
        blank=True,
        related_name='personeller'
    )
    ozel_durumu_aciklama = models.TextField(blank=True)
    engel_orani = models.PositiveSmallIntegerField(null=True, blank=True)
    vergi_indirimi = models.CharField(max_length=31, choices=ENGEL_DERECESI_DEGERLERI, blank=True)
    # İzin bilgileri
    memur_devreden_izin = models.FloatField(default=0)
    memur_hak_ettigi_izin = models.FloatField(default=0)
    # kalan_izin hesaplanacak, şimdilik yorum
    # İletişim bilgileri
    adres = models.TextField(blank=True)
    telefon = models.CharField(max_length=10, blank=True)
    eposta = models.EmailField(blank=True)
    # Ayrılış bilgileri
    ayrilma_tarihi = models.DateField(null=True, blank=True)
    ayrilma_nedeni = models.CharField(max_length=30, choices=AYRILMA_NEDENI_DEGERLERI, blank=True)
    ayrilma_detay = models.TextField(blank=True)
    # Diğer bilgiler
    dhy = models.BooleanField(default=False)
    sgk = models.BooleanField(default=False)
    dss = models.BooleanField(default=False)
    shcek = models.BooleanField(default=False)

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
    def burc(self):
        if not self.dogum_tarihi:
            return None
        # 'burc' template filter yoksa, string döndür
        from .valuelists import get_burc_for_date
        return get_burc_for_date(self.dogum_tarihi)

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
                return "Pasif (Geçici Görevde)" # More descriptive status
            return "Aktif"
        else:
            # For non-kadrolu, maybe active means they have an ongoing assignment?
            # Assuming similar logic: active if currently on an assignment.
            active_gorev = self.gecicigorev_set.filter(
                models.Q(gecici_gorev_bitis__isnull=True) | models.Q(gecici_gorev_bitis__gte=today),
                gecici_gorev_baslangic__lte=today
            ).exists()
            return "Aktif (Görevde)" if active_gorev else "Pasif (Görevde Değil)" # Or adjust as needed

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

    # Kalan izin hesaplaması için not:
    # @property
    # def kalan_izin(self):
    #     if self.memuriyet_durumu == "Memur (657)":
    #         return self.memur_devreden_izin + self.memur_hak_ettigi_izin - ... # mevcut yıl kullandığı izinler
    #     else:
    #         return ... # YillikIzinHakedis modeline göre hesaplanacak

    def __str__(self):
        return self.ad_soyad
