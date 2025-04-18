# Generated by Django 5.0.9 on 2025-04-15 20:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HizmetSunumAlani',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AlanAdi', models.CharField(max_length=100, verbose_name='Alan Adı')),
                ('AlanKodu', models.CharField(max_length=50, unique=True, verbose_name='Alan Kodu')),
            ],
            options={
                'verbose_name': 'Hizmet Sunum Alanı',
                'verbose_name_plural': 'Hizmet Sunum Alanları',
            },
        ),
        migrations.CreateModel(
            name='Personel',
            fields=[
                ('PersonelId', models.AutoField(primary_key=True, serialize=False)),
                ('PersonelAdi', models.CharField(max_length=50, verbose_name='Personel Adı')),
                ('PersonelSoyadi', models.CharField(max_length=50, verbose_name='Personel Soyadı')),
            ],
            options={
                'verbose_name': 'Personel',
                'verbose_name_plural': 'Personeller',
            },
        ),
        migrations.CreateModel(
            name='Birim',
            fields=[
                ('BirimId', models.AutoField(primary_key=True, serialize=False)),
                ('BirimAdi', models.CharField(max_length=100, verbose_name='Birim Adı')),
                ('KurumAdi', models.CharField(max_length=100, verbose_name='Kurum Adı')),
                ('HSAKodu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hizmet_sunum_app.hizmetsunumalani', verbose_name='Hizmet Sunum Alan Kodu')),
            ],
            options={
                'verbose_name': 'Birim',
                'verbose_name_plural': 'Birimler',
            },
        ),
        migrations.CreateModel(
            name='HizmetSunumCalismasi',
            fields=[
                ('CalismaId', models.AutoField(primary_key=True, serialize=False)),
                ('CreationTimestamp', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Zamanı')),
                ('Donem', models.DateField(verbose_name="Dönem (Ayın 1'i)")),
                ('HizmetBaslangicTarihi', models.DateField(verbose_name='Hizmet Başlangıç Tarihi')),
                ('HizmetBitisTarihi', models.DateField(verbose_name='Hizmet Bitiş Tarihi')),
                ('Sorumlu', models.BooleanField(default=False, verbose_name='Sorumlu')),
                ('Sertifika', models.BooleanField(default=False, verbose_name='Sertifika')),
                ('Aciklama', models.TextField(blank=True, null=True, verbose_name='Açıklama')),
                ('Kesinlestirme', models.BooleanField(default=False, verbose_name='Kesinleştirme')),
                ('CalisilanBirimId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hizmet_sunum_app.birim', verbose_name='Çalışılan Birim')),
                ('CreatedBy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Oluşturan')),
                ('PersonelId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hizmet_sunum_app.personel', verbose_name='Personel')),
            ],
            options={
                'verbose_name': 'Hizmet Sunum Çalışması',
                'verbose_name_plural': 'Hizmet Sunum Çalışmaları',
            },
        ),
    ]
