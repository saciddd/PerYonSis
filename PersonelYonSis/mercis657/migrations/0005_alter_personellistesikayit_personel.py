# Generated by Django 5.0.3 on 2025-06-02 19:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercis657', '0004_kurum_muduryardimcisi_ustbirim_birim_kurum_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personellistesikayit',
            name='personel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mercis657.personel'),
        ),
    ]
