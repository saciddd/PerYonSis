from django.db import models
from datetime import date, timedelta
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

class Birim(models.Model):
    BirimID = models.AutoField(primary_key=True)
    BirimAdi = models.CharField(max_length=100, unique=True)

    Kurum = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, blank=True)
    UstBirim = models.ForeignKey(UstBirim, on_delete=models.SET_NULL, null=True, blank=True)
    Idareci = models.ForeignKey(Idareci, on_delete=models.SET_NULL, null=True, blank=True)

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

    class Meta:
        unique_together = ('birim', 'yil', 'ay')
        verbose_name = 'Personel Listesi'
        verbose_name_plural = 'Personel Listeleri'

    def __str__(self):
        return f"{self.birim.BirimAdi} - {self.ay}/{self.yil}"

class PersonelListesiKayit(models.Model):
    liste = models.ForeignKey(PersonelListesi, on_delete=models.CASCADE, related_name='kayitlar')
    personel = models.ForeignKey('Personel', on_delete=models.CASCADE)

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
    PersonelTitle = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.PersonelName} ({self.PersonelTCKN})"

class Mesai(models.Model):
    MesaiID = models.AutoField(primary_key=True)
    Personel = models.ForeignKey('Personel', on_delete=models.CASCADE)
    MesaiDate = models.DateField(null=False)
    MesaiTanim = models.ForeignKey('Mesai_Tanimlari', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.Personel.PersonelName} - {self.MesaiDate}"

class Mesai_Tanimlari(models.Model):
    Saat = models.CharField(max_length=11)
    GunduzMesaisi = models.BooleanField(default=False)
    AksamMesaisi = models.BooleanField(default=False)
    GeceMesaisi = models.BooleanField(default=False)
    IseGeldi = models.BooleanField(default=False)
    SonrakiGuneSarkiyor = models.BooleanField(default=False)
    AraDinlenme = models.DurationField(null=True, blank=True)
    GecerliMesai = models.BooleanField(default=True)
    CKYS_BTF_Karsiligi = models.CharField(max_length=100, null=True, blank=True)
    Sure = models.DurationField(null=True, blank=True)

    def calculate_sure(self):
        """Mesai süresini (Sure) hesaplayan yöntem."""
        start, end = self.Saat.split(' ')
        start_time = self._parse_time(start)
        end_time = self._parse_time(end)

        if self.SonrakiGuneSarkiyor:
            end_time += timedelta(hours=24)

        total_time = end_time - start_time
        total_time -= self.AraDinlenme if self.AraDinlenme else timedelta(0)

        self.Sure = total_time


    def _parse_time(self, time_str):
        """'HH:MM' formatında bir saat dilimini datetime.time olarak döndürür."""
        hours, minutes = map(int, time_str.split(':'))
        return timedelta(hours=hours, minutes=minutes)

    def __str__(self):
        return self.Saat

class Izin(models.Model):
    ad = models.CharField(max_length=100, unique=True)
    kod = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.ad