from django.core.management.base import BaseCommand
from django.utils import timezone
from hekim_cizelge.models import ResmiTatil

class Command(BaseCommand):
    help = 'Test verileri oluşturur'

    def handle(self, *args, **options):
        # Resmi tatil test verileri
        tatiller = [
            {
                'tarih': '2024-01-01',
                'aciklama': 'Yılbaşı',
                'tip': 'TAM'
            },
            {
                'tarih': '2024-04-23',
                'aciklama': '23 Nisan Ulusal Egemenlik ve Çocuk Bayramı',
                'tip': 'TAM'
            },
            {
                'tarih': '2024-05-01',
                'aciklama': 'Emek ve Dayanışma Günü',
                'tip': 'TAM'
            },
            {
                'tarih': '2024-05-19',
                'aciklama': 'Atatürkü Anma Gençlik ve Spor Bayramı',
                'tip': 'TAM'
            }
        ]

        for tatil in tatiller:
            ResmiTatil.objects.get_or_create(
                TatilTarihi=tatil['tarih'],
                defaults={
                    'Aciklama': tatil['aciklama'],
                    'TatilTipi': tatil['tip']
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Test verileri başarıyla oluşturuldu'))
