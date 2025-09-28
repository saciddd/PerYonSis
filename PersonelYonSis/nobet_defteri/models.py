from PersonelYonSis.models import User
from django.db import models

class NobetTuru(models.Model):
    ad = models.CharField(max_length=100)  # Süpervizör, Nöbetçi Hekim, Memur, vs.
    aciklama = models.TextField(blank=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

class NobetDefteri(models.Model):
    tarih = models.DateField()
    nobet_turu = models.ForeignKey(NobetTuru, on_delete=models.CASCADE)
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan", related_name='nobet_defterleri_olusturan')
    aciklama = models.TextField(blank=True)  # Genel açıklama
    onayli = models.BooleanField(default=False)
    onaylayan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Onaylayan", related_name='nobet_defterleri_onaylayan')
    onay_tarihi = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tarih', 'nobet_turu')

    def __str__(self):
        return f"{self.nobet_turu} - {self.tarih}"

class NobetOlayKaydi(models.Model):
    defter = models.ForeignKey(NobetDefteri, on_delete=models.CASCADE, related_name='olaylar')
    saat = models.TimeField()
    konu = models.CharField(max_length=200)
    detay = models.TextField()
    onemli = models.BooleanField(default=False)
    ekleyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    eklenme_zamani = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.saat} - {self.konu}"

class KontrolSoru(models.Model):
    soru_metni = models.CharField(max_length=255)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.soru_metni

class KontrolFormu(models.Model):
    nobet_defteri = models.OneToOneField(
        NobetDefteri, on_delete=models.CASCADE, related_name="kontrol_formu"
    )
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Kontrol Formu - {self.nobet_defteri}"

class KontrolCevap(models.Model):
    form = models.ForeignKey(KontrolFormu, on_delete=models.CASCADE, related_name="cevaplar")
    soru = models.ForeignKey(KontrolSoru, on_delete=models.PROTECT)
    cevap = models.BooleanField(null=True, blank=True)  # Evet/Hayır
    aciklama = models.TextField(blank=True)

    def __str__(self):
        return f"{self.soru.soru_metni[:30]}... -> {self.cevap}"

class NobetciTekniker(models.Model):
    defter = models.ForeignKey(NobetDefteri, on_delete=models.CASCADE, related_name='teknikerler')
    tekniker_adi = models.CharField(max_length=100)
    gelis_saati = models.TimeField()
    ayrilis_saati = models.TimeField()

    class Meta:
        unique_together = ('defter', 'tekniker_adi')

    def __str__(self):
        return f"{self.tekniker_adi} - {self.defter.tarih}"