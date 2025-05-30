# Generated by Django 5.0.9 on 2025-05-04 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ik_core', '0003_gecicigorev_asil_kurumu'),
    ]

    operations = [
        migrations.CreateModel(
            name='OzelDurum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kod', models.CharField(max_length=30, unique=True)),
                ('ad', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='personel',
            name='ozel_durumu',
        ),
        migrations.AddField(
            model_name='personel',
            name='ozel_durumu',
            field=models.ManyToManyField(blank=True, related_name='personeller', to='ik_core.ozeldurum'),
        ),
    ]
