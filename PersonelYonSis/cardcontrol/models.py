from django.db import models

class Cihaz(models.Model):
    kapi_adi = models.CharField(max_length=100, verbose_name="Kapı Adı")
    ip = models.GenericIPAddressField(protocol='IPv4', verbose_name="IP Adresi")
    port = models.PositiveIntegerField(default=4370, verbose_name="Port")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")

    def __str__(self):
        return f"{self.kapi_adi} ({self.ip})"

    class Meta:
        verbose_name = "Cihaz"
        verbose_name_plural = "Cihazlar"


class CihazKullanici(models.Model):
    cihaz = models.ForeignKey(Cihaz, on_delete=models.CASCADE, related_name='kullanicilar', verbose_name="Cihaz")
    uid = models.PositiveIntegerField(verbose_name="UID")
    user_id = models.CharField(max_length=50, verbose_name="User ID")
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    card = models.CharField(max_length=50, blank=True, null=True, verbose_name="Kart No")
    privilege = models.IntegerField(default=0, verbose_name="Yetki")

    class Meta:
        verbose_name = "Cihaz Kullanıcısı"
        verbose_name_plural = "Cihaz Kullanıcıları"
        unique_together = ('cihaz', 'uid')  # Bir cihazda aynı UID tekrar edemez.

    def __str__(self):
        return f"{self.name} - {self.cihaz.kapi_adi}"

class CihazLog(models.Model):
    cihaz = models.ForeignKey(Cihaz, on_delete=models.CASCADE, related_name='logs', verbose_name="Cihaz")
    uid = models.PositiveIntegerField(verbose_name="UID") # User ID ile eşleşebilir
    user_id = models.CharField(max_length=50, verbose_name="User ID", blank=True, null=True)
    timestamp = models.DateTimeField(verbose_name="Zaman")
    status = models.IntegerField(verbose_name="Durum", default=0) # Giriş/Çıkış vb.
    verification = models.IntegerField(verbose_name="Doğrulama Türü", default=0)

    class Meta:
        verbose_name = "Cihaz Logu"
        verbose_name_plural = "Cihaz Logları"
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['cihaz']),
        ]

    def __str__(self):
        return f"{self.cihaz.kapi_adi} - {self.timestamp}"
