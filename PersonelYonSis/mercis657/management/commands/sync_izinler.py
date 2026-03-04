import os
import json
from django.conf import settings
from django.core.management.base import BaseCommand
from datetime import datetime, date, timedelta
from mercis657.models import Mesai, Personel, Izin
from PersonelYonSis.FMConnection.KDHIzin import IzinSorgula

def get_or_create_izin_turu(izin_adi):
    izin_obj, created = Izin.objects.get_or_create(
        fm_karsiligi=izin_adi,
        defaults={'ad': izin_adi}
    )
    return izin_obj

class Command(BaseCommand):
    help = 'Mevcut tarihten 30 gün öncesi ve sonrası için FileMaker üzerinden izinleri çekip Mesai tablosuna işler.'

    def handle(self, *args, **kwargs):
        today = date.today()
        baslangic = today - timedelta(days=30)
        bitis = today + timedelta(days=30)
        
        self.stdout.write(f"İzinler çekiliyor: {baslangic} - {bitis}...")
        
        try:
            izinler = IzinSorgula(
                baslangic=baslangic.strftime("%Y-%m-%d"),
                bitis=bitis.strftime("%Y-%m-%d")
            )
            
            if not izinler:
                self.stdout.write(self.style.WARNING("Belirtilen tarih aralığında izin bulunamadı."))
                return

            updated_count = 0
            
            # Veritabanı gecikmesini önlemek için tüm personeli çekelim
            personel_qs = Personel.objects.all()
            personel_map = {}
            for p in personel_qs:
                if p.PersonelTCKN:
                    # FileMaker'dan string veya number gelebilir
                    personel_map[str(p.PersonelTCKN)] = p
            
            for row in izinler:
                tckn, baslangic_tarihi, bitis_tarihi, izin_turu = row
                
                personel = personel_map.get(str(tckn))
                if not personel:
                    continue  # Sistemimizde olmayan bir personel ise atla
                
                # İzin türü objesini getir
                izin_obj = get_or_create_izin_turu(izin_turu)
                
                try:
                    start_date = datetime.strptime(str(baslangic_tarihi), "%Y-%m-%d").date()
                    # İzin bitiş günü dahil edilmediği için (genellikle FileMaker'da böyledir) 1 gün çıkarılıyor
                    end_date = datetime.strptime(str(bitis_tarihi), "%Y-%m-%d").date() - timedelta(days=1)
                except ValueError:
                    continue
                
                # Bu tarih aralığındaki Mesai kayıtlarını bul
                mesailer = Mesai.objects.filter(
                    Personel=personel,
                    MesaiDate__range=(start_date, end_date)
                )

                for mesai in mesailer:
                    if mesai.Izin != izin_obj:
                        mesai.Izin = izin_obj
                        mesai.SistemdekiIzin = True
                        mesai.MesaiTanim = None  # İzinli günde mesai olmaz
                        mesai.save(update_fields=["Izin", "MesaiTanim", "SistemdekiIzin"])
                        updated_count += 1
                    elif mesai.Izin == izin_obj and not mesai.SistemdekiIzin:
                        mesai.SistemdekiIzin = True
                        mesai.save(update_fields=["SistemdekiIzin"])
                        updated_count += 1
                        
            # Son güncellenme verisini dosyaya yaz
            sync_file_path = os.path.join(settings.BASE_DIR, 'mercis657', 'last_izin_sync.json')
            sync_data = {
                'time': datetime.now().strftime('%d.%m.%Y %H:%M'),
                'count': updated_count
            }
            try:
                with open(sync_file_path, 'w', encoding='utf-8') as f:
                    json.dump(sync_data, f)
            except Exception as file_exp:
                self.stdout.write(self.style.WARNING(f"Log dosyası yazılamadı: {str(file_exp)}"))

            self.stdout.write(self.style.SUCCESS(f"Başarıyla {updated_count} mesai kaydı güncellendi."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"İşlem sırasında hata oluştu: {str(e)}"))
