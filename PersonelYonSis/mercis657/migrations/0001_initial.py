# Generated by Django 5.0.9 on 2024-10-05 12:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Personel',
            fields=[
                ('PersonelID', models.BigIntegerField(primary_key=True, serialize=False)),
                ('PersonelName', models.CharField(max_length=100)),
                ('PersonelTitle', models.CharField(max_length=100, null=True)),
                ('BirthDate', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mesai',
            fields=[
                ('MesaiID', models.AutoField(primary_key=True, serialize=False)),
                ('MesaiDate', models.DateField()),
                ('MesaiData', models.CharField(max_length=11, null=True)),
                ('Personel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mercis657.personel')),
            ],
        ),
    ]
