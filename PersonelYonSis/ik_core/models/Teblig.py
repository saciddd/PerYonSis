from django.db import models


class TebligImzasi(models.Model):
    ad = models.CharField(max_length=50)
    metin = models.TextField()

    def __str__(self) -> str:
        return self.ad


class TebligMetni(models.Model):
    ad = models.CharField(max_length=100)
    metin = models.TextField()

    def __str__(self) -> str:
        return self.ad


