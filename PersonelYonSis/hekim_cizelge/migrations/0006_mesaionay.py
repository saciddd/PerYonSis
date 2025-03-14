# Generated by Django 5.1.6 on 2025-03-14 12:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hekim_cizelge', '0005_alter_birim_digerhizmetler_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MesaiOnay',
            fields=[
                ('OnayID', models.AutoField(primary_key=True, serialize=False)),
                ('OnayDurumu', models.IntegerField(choices=[(0, 'Beklemede'), (1, 'Onaylandı'), (2, 'Reddedildi')], default=0)),
                ('OnayTarihi', models.DateTimeField(auto_now_add=True)),
                ('Aciklama', models.TextField(blank=True, null=True)),
                ('Mesai', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='onaylar', to='hekim_cizelge.mesai')),
                ('Onaylayan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-OnayTarihi'],
            },
        ),
    ]
