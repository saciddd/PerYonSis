from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json
from .models import Mesai, PersonelListesiKayit

@login_required
def cizelge_yazdir(request):
    # Şimdilik boş, ileride PDF şablonu ile doldurulacak
    return HttpResponse("Yazdır PDF fonksiyonu hazırlanacak.", content_type="text/plain")

@login_required
def cizelge_kaydet(request):
    if request.method == 'POST':
        changes = json.loads(request.body)
        errors = []

        for key, mesai_tanim_id in changes.items():
            personel_id, mesai_date = key.split('_')
            mesai_date = datetime.strptime(mesai_date, "%Y-%m-%d").date()

            # Kayıtlı mı kontrol et
            if not PersonelListesiKayit.objects.filter(
                personel_id=personel_id,
                liste__yil=mesai_date.year,
                liste__ay=mesai_date.month
            ).exists():
                errors.append(f"Personel {personel_id} o ay listede değil.")
                continue

            # Aynı güne birden fazla kaydı zaten engelliyoruz (update_or_create)
            Mesai.objects.update_or_create(
                Personel_id=personel_id,
                MesaiDate=mesai_date,
                defaults={'MesaiTanim_id': mesai_tanim_id}
            )

        if errors:
            return JsonResponse({'status': 'partial', 'errors': errors})
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)

