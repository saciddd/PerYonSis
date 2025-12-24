from django.db import models


class DurumBelgesi(models.Model):
    ad = models.CharField(max_length=50)
    metin = models.TextField()

    def __str__(self) -> str:
        return self.ad

