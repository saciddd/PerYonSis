# Generated by Django 5.0.9 on 2025-06-24 21:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mercis657', '0007_kurum_aktif_muduryardimcisi_aktif_ustbirim_aktif'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MudurYardimcisi',
            new_name='Idareci',
        ),
        migrations.RenameField(
            model_name='birim',
            old_name='MudurYrd',
            new_name='Idareci',
        ),
    ]
