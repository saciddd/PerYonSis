import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PersonelYonSis.settings')
django.setup()

from mercis657.models import PersonelListesiKayit, Mesai
from mercis657.utils import hesapla_fazla_mesai

# Look for month and year that matches the image.
# The image shows days up to 28. Month 2 (February) has 28 days!
# Year would be 2026 if it's recent, or maybe 2025?
year = 2026
month = 2 # Feb has 28 days

# Find all users
plks = PersonelListesiKayit.objects.filter(donem_yil=year, donem_ay=month)
if not plks.exists():
    plks = PersonelListesiKayit.objects.all()

for plk in plks:
    try:
        y, m = plk.donem_yil, plk.donem_ay
        res = hesapla_fazla_mesai(plk, y, m)
        if res['fazla_mesai'] > 0:
            print(f"[{y}-{m}] Personel: {plk.personel.ad_soyad}, Gündüz: {res['normal_fazla_mesai']:.1f}, Gece: {res['normal_gece_fazla_mesai']:.1f}, Toplam: {res['fazla_mesai']:.1f}")
    except Exception as e:
        # print(e)
        pass
