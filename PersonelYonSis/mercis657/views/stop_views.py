from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from ..models import StopKaydi, Mesai
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from django.utils import timezone
import datetime
from datetime import timedelta

@login_required
def stop_ekle(request, mesai_id):
    if not request.user.has_permission('ÇS 657 Stop Kaydı Ekleme'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    mesai = get_object_or_404(Mesai, pk=mesai_id)
    # GET: render modal partial with existing stops (if any)
    if request.method == "GET":
        # ensure related person and mesai tanim prefetched
        mesai = Mesai.objects.select_related('Personel', 'MesaiTanim').prefetch_related('mercis657_stoplar').get(pk=mesai_id)
        return render(request, "mercis657/stop_modal.html", {"mesai": mesai})

    # POST: create a StopKaydi
    if request.method == "POST":
        baslangic_raw = request.POST.get("StopBaslangic")  # expected 'HH:MM' or 'HH:MM:SS'
        bitis_raw = request.POST.get("StopBitis")
        if not baslangic_raw or not bitis_raw:
            return JsonResponse({'status': 'error', 'message': 'Zaman verisi eksik.'}, status=400)

        try:
            # parse time strings
            bas_time = datetime.time.fromisoformat(baslangic_raw)
            bit_time = datetime.time.fromisoformat(bitis_raw)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Zaman formatı okunamadı.'}, status=400)

        # combine with mesai date
        mesai_date = mesai.MesaiDate
        bas_dt = datetime.datetime.combine(mesai_date, bas_time)
        bit_dt = datetime.datetime.combine(mesai_date, bit_time)

        # If end is earlier or equal to start, assume next day
        if bit_dt <= bas_dt:
            bit_dt = bit_dt + timedelta(days=1)

        # make timezone-aware if naive
        if timezone.is_naive(bas_dt):
            bas_dt = timezone.make_aware(bas_dt, timezone.get_current_timezone())
        if timezone.is_naive(bit_dt):
            bit_dt = timezone.make_aware(bit_dt, timezone.get_current_timezone())

        stop = StopKaydi.objects.create(
            mesai=mesai,
            StopBaslangic=bas_dt,
            StopBitis=bit_dt,
            created_by=request.user,
        )
        # return sure in hours
        return JsonResponse({"status": "success", "sure": stop.Sure})


@login_required
@require_POST
def stop_sil(request, stop_id):
    if not request.user.has_permission('ÇS 657 Stop Kaydı Ekleme'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    stop = get_object_or_404(StopKaydi, pk=stop_id)
    stop.delete()
    return JsonResponse({"status": "deleted"})
