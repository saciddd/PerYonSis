from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from ..models import EkMesai, Mesai
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
import datetime
from datetime import timedelta

@login_required
def ek_mesai_ekle(request, mesai_id):
    if not request.user.has_permission('ÇS 657 Stop Kaydı Ekleme'):
        messages.error(request, "Ek Mesai Ekleme yetkiniz yok.")
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    mesai = get_object_or_404(Mesai, pk=mesai_id)
    
    if request.method == "GET":
        mesai = Mesai.objects.select_related('Personel', 'MesaiTanim').prefetch_related('mercis657_ek_mesailer').get(pk=mesai_id)
        return render(request, "mercis657/ek_mesai_modal.html", {"mesai": mesai})

    if request.method == "POST":
        baslangic_raw = request.POST.get("Baslangic")
        bitis_raw = request.POST.get("Bitis")
        aciklama = request.POST.get("Aciklama")
        riskli = request.POST.get("Riskli") == 'on'
        
        if not baslangic_raw or not bitis_raw:
            return JsonResponse({'status': 'error', 'message': 'Zaman verisi eksik.'}, status=400)

        try:
            bas_time = datetime.time.fromisoformat(baslangic_raw)
            bit_time = datetime.time.fromisoformat(bitis_raw)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Zaman formatı okunamadı.'}, status=400)

        mesai_date = mesai.MesaiDate
        bas_dt = datetime.datetime.combine(mesai_date, bas_time)
        bit_dt = datetime.datetime.combine(mesai_date, bit_time)

        if bit_dt <= bas_dt:
            bit_dt = bit_dt + timedelta(days=1)

        if timezone.is_naive(bas_dt):
            bas_dt = timezone.make_aware(bas_dt, timezone.get_current_timezone())
        if timezone.is_naive(bit_dt):
            bit_dt = timezone.make_aware(bit_dt, timezone.get_current_timezone())

        ek_mesai = EkMesai.objects.create(
            mesai=mesai,
            Baslangic=bas_dt,
            Bitis=bit_dt,
            Aciklama=aciklama,
            Riskli=riskli,
            created_by=request.user,
        )
        return JsonResponse({"status": "success", "sure": ek_mesai.Sure})

@login_required
@require_POST
def ek_mesai_sil(request, ek_mesai_id):
    if not request.user.has_permission('ÇS 657 Stop Kaydı Ekleme'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    ek_mesai = get_object_or_404(EkMesai, pk=ek_mesai_id)
    ek_mesai.delete()
    return JsonResponse({"status": "deleted"})
