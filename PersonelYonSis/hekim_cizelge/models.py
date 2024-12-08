from django.db import models

class Birim(models.Model):
    BirimID = models.AutoField(primary_key=True)
    BirimAdi = models.CharField(max_length=100, unique=True)
    VarsayilanHizmet = models.ForeignKey(
        'Hizmet',
        on_delete=models.SET_NULL,
        null=True,
        related_name='varsayilan_hizmet_birimleri'
    )
    DigerHizmetler = models.ManyToManyField(
        'Hizmet',
        related_name='diger_hizmet_birimleri'
    )

    def __str__(self):
        return self.BirimAdi

class Hizmet(models.Model):
    STANDART = 'Standart'
    NOBET = 'Nöbet'
    ICAP = 'İcap'
    HIZMET_TIPLERI = [
        (STANDART, 'Standart'),
        (NOBET, 'Nöbet'),
        (ICAP, 'İcap'),
    ]

    HizmetID = models.AutoField(primary_key=True)
    HizmetName = models.CharField(max_length=100, unique=True)
    HizmetTipi = models.CharField(max_length=10, choices=HIZMET_TIPLERI)
    HizmetSuresi = models.DurationField(help_text="Hizmet süresi, örn: 8 saat için '8:00:00'")

    def __str__(self):
        return f"{self.HizmetName} ({self.HizmetTipi})"

class Personel(models.Model):
    PersonelID = models.AutoField(primary_key=True)
    PersonelName = models.CharField(max_length=100)  # Ad Soyad
    PersonelTitle = models.CharField(max_length=50)  # Unvan (ör. Uzman Tabip)
    PersonelBranch = models.CharField(max_length=100)  # Branş (ör. İç Hastalıkları)
    birim = models.ManyToManyField(Birim, through='PersonelBirim')

    def __str__(self):
        return f"{self.PersonelName} ({self.PersonelTitle})"

class PersonelBirim(models.Model):
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE)
class Mesai(models.Model):
    MesaiID = models.AutoField(primary_key=True)
    Personel = models.ForeignKey('Personel', on_delete=models.CASCADE)
    MesaiDate = models.DateField(null=False)
    Hizmetler = models.ManyToManyField('Hizmet', related_name='mesai_hizmetleri')

    def __str__(self):
        return f"Mesai {self.MesaiDate} - {self.Personel.PersonelName}"
