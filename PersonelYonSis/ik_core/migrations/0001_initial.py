# Generated by Django 5.0.9 on 2025-05-02 20:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brans',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Kurum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Unvan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.CharField(max_length=100)),
                ('sinif', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Personel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tc_kimlik_no', models.CharField(max_length=11, unique=True)),
                ('ad', models.CharField(max_length=50)),
                ('soyad', models.CharField(max_length=50)),
                ('sicil_no', models.CharField(blank=True, max_length=30)),
                ('dogum_tarihi', models.DateField(blank=True, null=True)),
                ('cinsiyet', models.CharField(choices=[('Erkek', 'Erkek'), ('Kadin', 'Kadın')], max_length=6)),
                ('kadrolu_personel', models.BooleanField(default=True)),
                ('atama_karar_tarihi', models.DateField(blank=True, null=True)),
                ('atama_karar_no', models.CharField(blank=True, max_length=50)),
                ('goreve_baslama_tarihi', models.DateField(blank=True, null=True)),
                ('memuriyete_baslama_tarihi', models.DateField(blank=True, null=True)),
                ('kamu_baslangic_tarihi', models.DateField(blank=True, null=True)),
                ('teskilat', models.CharField(choices=[('657/4B (663 Sayılı KHK 45/A Sözleşmeli)', '657/4B (663 Sayılı KHK 45/A Sözleşmeli)'), ('Döner Sermaye', 'Döner Sermaye'), ('İşçi Personel (Genel Bütçe)', 'İşçi Personel (Genel Bütçe)'), ('İşçi Personel 696 (Döner Sermaye)', 'İşçi Personel 696 (Döner Sermaye)'), ('Sözleşmeli (4924)', 'Sözleşmeli (4924)'), ('Taşra', 'Taşra')], max_length=50)),
                ('emekli_sicil_no', models.CharField(blank=True, max_length=30)),
                ('tahsil_durumu', models.CharField(choices=[('Okuryazar', 'Okuryazar'), ('İlkokul', 'İlkokul'), ('Ortaokul', 'Ortaokul'), ('İlköğretim', 'İlköğretim'), ('Lise', 'Lise'), ('Önlisans', 'Önlisans'), ('Lisans', 'Lisans'), ('Yük. Öğr.(5 Yıl)', 'Yük. Öğr.(5 Yıl)'), ('Lisans Sonrası 1 Yıl', 'Lisans Sonrası 1 Yıl'), ('Yüksek Lisans', 'Yüksek Lisans'), ('Diş Hekimliği', 'Diş Hekimliği'), ('Tıp Fakültesi', 'Tıp Fakültesi'), ('Tıpta Uzmanlık', 'Tıpta Uzmanlık')], max_length=30)),
                ('aile_hek_sozlesmesi', models.BooleanField(default=False)),
                ('mazeret_durumu', models.CharField(blank=True, choices=[('Saglik', 'Sağlık'), ('Egitim', 'Eğitim'), ('EsDurumu', 'Eş Durumu'), ('AileBirligiDagilmasi', 'Aile Birliğinin Dağılması')], max_length=30)),
                ('mazeret_baslangic', models.DateField(blank=True, null=True)),
                ('mazeret_bitis', models.DateField(blank=True, null=True)),
                ('ozel_durumu', models.CharField(blank=True, choices=[('Engelli', 'Engelli'), ('Gazi', 'Gazi'), ('SehitYakini', 'Şehit Yakını'), ('BakmaklaYukumlu', 'Bakmakla Yükümlü')], max_length=30)),
                ('ozel_durumu_aciklama', models.TextField(blank=True)),
                ('engel_orani', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('vergi_indirimi', models.CharField(blank=True, choices=[('1.Derece Engelli (%80 ve üzeri)', '1.Derece Engelli (%80 ve üzeri)'), ('2.Derece Engelli (%60-79)', '2.Derece Engelli (%60-79)'), ('3.Derece Engelli (%40-59)', '3.Derece Engelli (%40-59)')], max_length=31)),
                ('memur_devreden_izin', models.FloatField(default=0)),
                ('memur_hak_ettigi_izin', models.FloatField(default=0)),
                ('adres', models.TextField(blank=True)),
                ('telefon', models.CharField(blank=True, max_length=10)),
                ('eposta', models.EmailField(blank=True, max_length=254)),
                ('ayrilma_tarihi', models.DateField(blank=True, null=True)),
                ('ayrilma_nedeni', models.CharField(blank=True, choices=[('Emeklilik', 'Emeklilik'), ('Tayin', 'Tayin'), ('TUS', 'TUS'), ('Diger', 'Diğer')], max_length=30)),
                ('ayrilma_detay', models.TextField(blank=True)),
                ('dhy', models.BooleanField(default=False)),
                ('sgk', models.BooleanField(default=False)),
                ('dss', models.BooleanField(default=False)),
                ('shcek', models.BooleanField(default=False)),
                ('brans', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ik_core.brans')),
                ('fiili_gorev_yeri', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fiili_gorev_personelleri', to='ik_core.kurum')),
                ('kadro_yeri', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kadro_personelleri', to='ik_core.kurum')),
                ('kurum', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='kurum_personelleri', to='ik_core.kurum')),
                ('unvan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ik_core.unvan')),
            ],
        ),
        migrations.CreateModel(
            name='GeciciGorev',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gecici_gorev_baslangic', models.DateField()),
                ('gecici_gorev_bitis', models.DateField(blank=True, null=True)),
                ('gorevlendirildigi_birim', models.CharField(max_length=150)),
                ('personel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gecicigorev_set', to='ik_core.personel')),
            ],
        ),
        migrations.AddField(
            model_name='brans',
            name='unvan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ik_core.unvan'),
        ),
    ]
