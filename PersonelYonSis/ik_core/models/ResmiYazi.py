from django.db import models

class ResmiYazi(models.Model):
    ad = models.CharField(max_length=50)
    metin = models.TextField()
    ilgi = models.CharField(max_length=100, blank=True, null=True)
    ek = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self) -> str:
        return self.ad
