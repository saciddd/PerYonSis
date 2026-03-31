from django.db import models

class Sertifika(models.Model):
    personel = models.ForeignKey('hizmet_sunum_app.Personel', on_delete=models.CASCADE, related_name='sertifikalar', verbose_name='Personel')
    sertifika_aciklamasi = models.TextField(verbose_name='Sertifika Açıklaması')
    baslangic_tarihi = models.DateField(verbose_name='Başlangıç Tarihi')
    bitis_tarihi = models.DateField(verbose_name='Bitiş Tarihi')
    alanda_kullaniliyor = models.BooleanField(default=False, verbose_name='Alanda Kullanılıyor')

    class Meta:
        verbose_name = 'Sertifika'
        verbose_name_plural = 'Sertifikalar'

    def __str__(self):
        return f"{self.personel} - {self.sertifika_aciklamasi}"
