from django.db import models
from PersonelYonSis.models import User

class UstBirim(models.Model):
    ad = models.CharField(max_length=100, verbose_name="Üst Birim Adı")
    
    class Meta:
        verbose_name = "Üst Birim"
        verbose_name_plural = "Üst Birimler"
        ordering = ['ad']
    
    def __str__(self):
        return self.ad

class Bina(models.Model):
    ad = models.CharField(max_length=50, verbose_name="Bina Adı")
    
    class Meta:
        verbose_name = "Bina"
        verbose_name_plural = "Binalar"
        ordering = ['ad']
    
    def __str__(self):
        return self.ad
    
    @property
    def birim_sayisi(self):
        return self.birim_set.count()

class Birim(models.Model):
    bina = models.ForeignKey(Bina, on_delete=models.CASCADE, verbose_name="Bina")
    ust_birim = models.ForeignKey(UstBirim, on_delete=models.CASCADE, verbose_name="Üst Birim")
    ad = models.CharField(max_length=50, verbose_name="Birim Adı")
    birim_tipi = models.CharField(max_length=50, verbose_name="Birim Tipi")
    
    class Meta:
        verbose_name = "Birim"
        verbose_name_plural = "Birimler"
        ordering = ['ust_birim__ad', 'ad']
    
    def __str__(self):
        return f"{self.ad} ({self.bina.ad})"

class PersonelBirim(models.Model):
    personel = models.ForeignKey('ik_core.Personel', on_delete=models.CASCADE, verbose_name="Personel")
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE, verbose_name="Birim")
    gecis_tarihi = models.DateField(verbose_name="Geçiş Tarihi")
    sorumlu = models.BooleanField(default=False, verbose_name="Sorumlu")
    not_text = models.CharField(max_length=100, blank=True, null=True, verbose_name="Not")
    creation_timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Zamanı")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan")
    
    class Meta:
        verbose_name = "Personel Birim"
        verbose_name_plural = "Personel Birimler"
        ordering = ['-gecis_tarihi', '-creation_timestamp']
    
    def __str__(self):
        return f"{self.personel.ad_soyad} - {self.birim.ad} ({self.gecis_tarihi})"
