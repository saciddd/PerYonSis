from django.db import models
from datetime import date, timedelta

class Personel(models.Model):
    PersonelID = models.BigIntegerField(primary_key=True)
    PersonelName = models.CharField(max_length=100, null=False)
    PersonelTitle = models.CharField(max_length=100, null=True)
    BirthDate = models.DateField(null=True)

    def Age(self):
        if self.BirthDate:
            today = date.today()
            return today.year - self.BirthDate.year - ((today.month, today.day) < (self.BirthDate.month, self.BirthDate.day))
        return None

    def __str__(self):
        return self.PersonelName

class Mesai(models.Model):
    MesaiID = models.AutoField(primary_key=True)
    Personel = models.ForeignKey('Personel', on_delete=models.CASCADE)
    MesaiDate = models.DateField(null=False)
    MesaiTanim = models.ForeignKey('Mesai_Tanimlari', on_delete=models.CASCADE, null=True)  # Relation to Mesai_Tanimlari

    def __str__(self):
        return f"{self.Personel.PersonelName} - {self.MesaiDate}"

class Mesai_Tanimlari(models.Model):
    Saat = models.CharField(max_length=11)  # Saat aralığı '08:00 16:00' olarak güncellendi
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
        start, end = self.Saat.split(' ')  # '08:00 16:00' formatında boşlukla böl
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