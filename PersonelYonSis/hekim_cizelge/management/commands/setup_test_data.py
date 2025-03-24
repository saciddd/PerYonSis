from django.core.management.base import BaseCommand
from hekim_cizelge.models import Hizmet, Birim, Personel, PersonelBirim

class Command(BaseCommand):
    help = 'Test verileri oluşturur'

    def handle(self, *args, **kwargs):
        # Örnek hizmetler
        hizmetler = [
            {
                'name': 'Poliklinik',
                'type': Hizmet.STANDART,
                'sure_hafta_ici': 480,  # 8 saat
                'sure_hafta_sonu': None
            },
            {
                'name': 'Acil Nöbet',
                'type': Hizmet.NOBET,
                'sure_hafta_ici': 960,  # 16 saat
                'sure_hafta_sonu': 1440,  # 24 saat
                'nobet_ertesi_izinli': True
            },
            {
                'name': 'İcap Nöbeti',
                'type': Hizmet.ICAP,
                'sure_hafta_ici': 960,
                'sure_hafta_sonu': 1440
            }
        ]

        for h in hizmetler:
            hizmet, created = Hizmet.objects.get_or_create(
                HizmetName=h['name'],
                defaults={
                    'HizmetTipi': h['type'],
                    'HizmetSuresiHaftaIci': h['sure_hafta_ici'],
                    'HizmetSuresiHaftaSonu': h['sure_hafta_sonu'],
                    'NobetErtesiIzinli': h.get('nobet_ertesi_izinli', False)
                }
            )
            if created:
                self.stdout.write(f'Hizmet oluşturuldu: {hizmet.HizmetName}')

        # Örnek birim
        poliklinik_hizmeti = Hizmet.objects.get(HizmetName='Poliklinik')
        birim, created = Birim.objects.get_or_create(
            BirimAdi='Dahiliye',
            defaults={'VarsayilanHizmet': poliklinik_hizmeti}
        )
        if created:
            self.stdout.write(f'Birim oluşturuldu: {birim.BirimAdi}')
            # Diğer hizmetleri ekle
            birim.DigerHizmetler.set(Hizmet.objects.exclude(HizmetID=poliklinik_hizmeti.HizmetID))

        # Örnek personel
        personel = Personel.objects.get_or_create(
            PersonelName='Dr. Test Hekim',
            defaults={
                'PersonelTitle': 'Uzman Tabip',
                'PersonelBranch': 'İç Hastalıkları'
            }
        )[0]
        PersonelBirim.objects.get_or_create(personel=personel, birim=birim)
        self.stdout.write(f'Personel oluşturuldu: {personel.PersonelName}')
