from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile_657')
    tc = models.CharField(max_length=11, unique=True)
    authorized_units = models.TextField()  # Yetkili olunan birimler

    def __str__(self):
        return self.user.username

class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_657')
    name = models.CharField(max_length=100)
    date = models.DateField()
    data = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.date}"
