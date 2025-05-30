# Generated by Django 5.0.9 on 2025-05-25 20:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ik_core', '0005_alter_personel_teskilat'),
        ('mutemet_app', '0004_icratakibi_icra_turu_alter_icratakibi_durum'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='icratakibi',
            name='silme_isteyen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='silme_istegi_icralar', to=settings.AUTH_USER_MODEL, verbose_name='Silme İsteyen'),
        ),
        migrations.AlterField(
            model_name='sendikauyelik',
            name='hareket_tipi',
            field=models.CharField(choices=[('GIRIS', 'Giriş'), ('CIKIS', 'Çıkış')], max_length=10),
        ),
        migrations.CreateModel(
            name='SilinenIcraTakibi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icra_id', models.IntegerField()),
                ('icra_vergi_dairesi_no', models.CharField(max_length=50)),
                ('icra_dairesi', models.CharField(max_length=100)),
                ('dosya_no', models.CharField(max_length=50)),
                ('icra_dairesi_banka', models.CharField(max_length=100)),
                ('icra_dairesi_hesap_no', models.CharField(max_length=50)),
                ('alacakli', models.CharField(max_length=100)),
                ('alacakli_vekili', models.CharField(blank=True, max_length=100, null=True)),
                ('tarihi', models.DateField()),
                ('tutar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('durum', models.CharField(max_length=10)),
                ('icra_turu', models.CharField(max_length=10)),
                ('silinme_tarihi', models.DateTimeField(auto_now_add=True)),
                ('personel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ik_core.personel')),
                ('silen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='silinen_icralari_silen', to=settings.AUTH_USER_MODEL)),
                ('silme_isteyen', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='yedek_silme_isteyen', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Silinen İcra Takibi',
                'verbose_name_plural': 'Silinen İcra Takipleri',
            },
        ),
    ]
