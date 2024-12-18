# Generated by Django 5.0.9 on 2024-12-18 18:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hekim_cizelge', '0003_remove_personel_personelbirimid_personelbirim_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBirim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yetkili_kullanicilar', to='hekim_cizelge.birim')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='yetkili_birimler', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'birim')},
            },
        ),
    ]