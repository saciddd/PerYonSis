# Generated by Django 5.0.9 on 2025-04-26 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hekim_cizelge', '0004_alter_izin_mesaidendus'),
    ]

    operations = [
        migrations.AddField(
            model_name='resmitatil',
            name='ArefeMi',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='resmitatil',
            name='BayramAdi',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='resmitatil',
            name='BayramMi',
            field=models.BooleanField(default=False),
        ),
    ]
