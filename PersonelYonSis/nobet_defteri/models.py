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
