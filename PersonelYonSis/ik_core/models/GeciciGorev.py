from django.db import models
from .personel import Personel

class GeciciGorev(models.Model):
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE, related_name='gecicigorev_set')
    # GECICI_GOREV_TIPI alanı önemli, silinmeyecek!
    GECICI_GOREV_TIPI = (
        ('Gidis', 'Gidiş'),
        ('Gelis', 'Geliş'),
    )
    gecici_gorev_tipi = models.CharField(max_length=10, choices=GECICI_GOREV_TIPI, default='Gidis')
    gecici_gorev_baslangic = models.DateField()
    gecici_gorev_bitis = models.DateField(null=True, blank=True)
    asil_kurumu = models.CharField(max_length=150)
    gorevlendirildigi_birim = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.personel.full_name} - {self.gorevlendirildigi_birim} ({self.gecici_gorev_baslangic} - {self.gecici_gorev_bitis or 'devam'})"
