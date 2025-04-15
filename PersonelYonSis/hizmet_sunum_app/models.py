from django.db import models
from PersonelYonSis.models import User

class Personel(models.Model):
    PersonelId = models.AutoField(primary_key=True)
    PersonelAdi = models.CharField(max_length=50, verbose_name="Personel Adı")
    PersonelSoyadi = models.CharField(max_length=50, verbose_name="Personel Soyadı")

    class Meta:
        verbose_name = "Personel"
        verbose_name_plural = "Personeller"

    def __str__(self):
        return f"{self.PersonelAdi} {self.PersonelSoyadi}"

class HizmetSunumAlani(models.Model):
    AlanAdi = models.CharField(max_length=100, verbose_name="Alan Adı")
    AlanKodu = models.CharField(max_length=50, unique=True, verbose_name="Alan Kodu")

    class Meta:
        verbose_name = "Hizmet Sunum Alanı"
        verbose_name_plural = "Hizmet Sunum Alanları"

    def __str__(self):
        return f"{self.AlanAdi} ({self.AlanKodu})"

class Birim(models.Model):
    BirimId = models.AutoField(primary_key=True)
    BirimAdi = models.CharField(max_length=100, verbose_name="Birim Adı")
    KurumAdi = models.CharField(max_length=100, verbose_name="Kurum Adı")
    HSAKodu = models.ForeignKey(HizmetSunumAlani, on_delete=models.CASCADE, verbose_name="Hizmet Sunum Alan Kodu")

    class Meta:
        verbose_name = "Birim"
        verbose_name_plural = "Birimler"

    def __str__(self):
        return f"{self.BirimAdi} - {self.KurumAdi}"

class HizmetSunumCalismasi(models.Model):
    CalismaId = models.AutoField(primary_key=True)
    CreationTimestamp = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Zamanı")
    CreatedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan")
    CalisilanBirimId = models.ForeignKey(Birim, on_delete=models.CASCADE, verbose_name="Çalışılan Birim")
    Donem = models.DateField(verbose_name="Dönem (Ayın 1'i)")
    PersonelId = models.ForeignKey(Personel, on_delete=models.CASCADE, verbose_name="Personel")
    HizmetBaslangicTarihi = models.DateField(verbose_name="Hizmet Başlangıç Tarihi")
    HizmetBitisTarihi = models.DateField(verbose_name="Hizmet Bitiş Tarihi")
    Sorumlu = models.BooleanField(default=False, verbose_name="Sorumlu")
    Sertifika = models.BooleanField(default=False, verbose_name="Sertifika")
    Aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    Kesinlestirme = models.BooleanField(default=False, verbose_name="Kesinleştirme")

    class Meta:
        verbose_name = "Hizmet Sunum Çalışması"
        verbose_name_plural = "Hizmet Sunum Çalışmaları"

    def __str__(self):
        return f"{self.PersonelId} - {self.CalisilanBirimId} ({self.Donem})"
