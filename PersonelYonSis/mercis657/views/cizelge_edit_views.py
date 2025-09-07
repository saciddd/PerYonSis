from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json
from ..models import Mesai, PersonelListesiKayit, MesaiYedek, Mesai_Tanimlari, Izin

@login_required
def cizelge_yazdir(request):
    # Şimdilik boş, ileride PDF şablonu ile doldurulacak
    return HttpResponse("Yazdır PDF fonksiyonu hazırlanacak.", content_type="text/plain")

@login_required
def cizelge_kaydet(request):
    if request.method == 'POST':
        changes = json.loads(request.body)
        errors = []

        for key, data in changes.items():
            personel_id, mesai_date = key.split('_')
            mesai_date = datetime.strptime(mesai_date, "%Y-%m-%d").date()
            mesai_tanim_id = data.get('mesaiId')
            izin_id = data.get('izinId')

            # Kayıtlı mı kontrol et
            if not PersonelListesiKayit.objects.filter(
                personel_id=personel_id,
                liste__yil=mesai_date.year,
                liste__ay=mesai_date.month
            ).exists():
                errors.append(f"Personel {personel_id} o ay listede değil.")
                continue

            # Mevcut mesai kaydını bul
            try:
                existing_mesai = Mesai.objects.get(
                    Personel_id=personel_id,
                    MesaiDate=mesai_date
                )
                
                # Değişiklik var mı kontrol et
                mesai_changed = existing_mesai.MesaiTanim_id != mesai_tanim_id
                izin_changed = existing_mesai.Izin_id != izin_id
                
                if mesai_changed or izin_changed:
                    # Mevcut değerleri yedekle
                    if existing_mesai.MesaiTanim_id or existing_mesai.Izin_id:
                        MesaiYedek.objects.create(
                            mesai=existing_mesai,
                            MesaiTanim_id=existing_mesai.MesaiTanim_id,
                            Izin_id=existing_mesai.Izin_id,
                            created_by=request.user
                        )
                    
                    # Yeni değerleri kaydet
                    existing_mesai.MesaiTanim_id = mesai_tanim_id
                    existing_mesai.Izin_id = izin_id
                    existing_mesai.Degisiklik = False  # Değişiklik işlendi
                    existing_mesai.save()
                    
            except Mesai.DoesNotExist:
                # Yeni mesai kaydı oluştur
                Mesai.objects.create(
                    Personel_id=personel_id,
                    MesaiDate=mesai_date,
                    MesaiTanim_id=mesai_tanim_id,
                    Izin_id=izin_id,
                    Degisiklik=False
                )

        if errors:
            return JsonResponse({'status': 'partial', 'errors': errors})
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)

