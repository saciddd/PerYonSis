from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ..models import Birim, PersonelListesi, Mesai, Bildirim
from ..utils import get_turkish_month_name, hesapla_riskli_calisma
import json
from datetime import date
import calendar

@login_required
def riskli_calisma_yonetim(request, birim_id):
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
         return HttpResponseForbidden("Yetkiniz yok.")
    
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
    except (ValueError, TypeError):
        today = date.today()
        year = today.year
        month = today.month

    birim = get_object_or_404(Birim, pk=birim_id)
    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
    
    donem_baslangic = date(year, month, 1)
    
    # Days info
    days_in_month = calendar.monthrange(year, month)[1]
    days = []
    for d in range(1, days_in_month + 1):
        dt = date(year, month, d)
        days.append({
            'day': d,
            'date_str': dt.strftime('%Y-%m-%d'),
            'is_weekend': dt.weekday() >= 5
        })
        
    personel_data = []
    if liste:
        kayitlar = liste.kayitlar.select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname')
        
        # Fetch Mesai records
        # Efficiently fetching all mesai for all personnel in the list for this month
        personel_ids = [k.personel.PersonelID for k in kayitlar]
        mesailer = Mesai.objects.filter(
            Personel__PersonelID__in=personel_ids,
            MesaiDate__year=year, 
            MesaiDate__month=month
        )

        mesai_map = {}
        for m in mesailer:
            pid = m.Personel_id
            d_str = m.MesaiDate.strftime('%Y-%m-%d')
            if pid not in mesai_map: mesai_map[pid] = {}
            mesai_map[pid][d_str] = m
            
        # Fetch existing Bildirim records for quick stat
        bildirimler = Bildirim.objects.filter(
            Personel__PersonelID__in=personel_ids,
            DonemBaslangic=donem_baslangic,
            SilindiMi=False
        )
        bildirim_map = {b.Personel_id: b for b in bildirimler}

        for kayit in kayitlar:
            p = kayit.personel
            p_mesailer = mesai_map.get(p.PersonelID, {})
            # Removed Bildirim based total riskli calculation logic
            
            # Recalculate Total Risk using utility function
            total_riskli = float(hesapla_riskli_calisma(kayit, year, month))
            
            day_status = {}
            for day_info in days:
                d_str = day_info['date_str']
                mesai = p_mesailer.get(d_str)
                risk_status = 'none'
                has_mesai = False
                mesai_id = None
                is_clickable = False
                
                if mesai:
                    has_mesai = True
                    mesai_id = mesai.MesaiID
                    risk_status = mesai.riskli_calisma or 'none'
                    
                    # Only clickable if MesaiTanim exists AND not Izin
                    if mesai.MesaiTanim and not mesai.Izin:
                        is_clickable = True
                
                day_status[d_str] = {
                    'has_mesai': has_mesai,
                    'risk_status': risk_status,
                    'mesai_id': mesai_id,
                    'is_clickable': is_clickable
                }

            personel_data.append({
                'id': p.PersonelID,
                'name': f"{p.PersonelName} {p.PersonelSurname}",
                'total_riskli': total_riskli,
                'days': day_status
            })

    context = {
        'birim': birim,
        'year': year,
        'month': month,
        'days': days,
        'personel_data': personel_data,
        'month_name': get_turkish_month_name(month)
    }
    return render(request, 'mercis657/riskli_calisma_yonetim.html', context)

@login_required
@require_POST
def riskli_calisma_kaydet(request):
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
         return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
         
    try:
        data = json.loads(request.body)
        updates = data.get('updates', []) 
        bulk_action = data.get('bulk_action') # 'all_full', 'all_clear' for specific filters
        
        # 'updates' contains individual cell changes: {mesai_id: X, status: Y}
        # or bulk changes can be handled by logic here.
        
        # 1. Process explicit updates
        for up in updates:
            mid = up.get('mesai_id')
            status = up.get('status') # 'none', 'full', 'nobet'
            
            if not mid: continue
            
            mesai = Mesai.objects.filter(MesaiID=mid).first()
            if mesai:
                if status == 'none':
                    mesai.riskli_calisma = None
                elif status in [Mesai.RISKLI_TAM, Mesai.RISKLI_NOBET]:
                    mesai.riskli_calisma = status
                mesai.save()
        
        # 2. Process bulk actions if provided
        if bulk_action:
             # Expects params to scope the bulk action
             target_type = data.get('target_type') # 'personel' or 'all'
             personel_id = data.get('personel_id')
             year = data.get('year')
             month = data.get('month')
             birim_id = data.get('birim_id')
             
             if not (year and month and birim_id):
                 return JsonResponse({'status': 'error', 'message': 'Eksik parametreler'}, status=400)
             
             # Safer query via PersonelListesi
             liste = PersonelListesi.objects.filter(birim_id=birim_id, yil=year, ay=month).first()
             if not liste:
                 return JsonResponse({'status': 'error', 'message': 'Liste bulunamadı'}, status=404)
                 
             personel_ids = liste.kayitlar.values_list('personel_id', flat=True)
             
             qs = Mesai.objects.filter(
                 MesaiDate__year=year,
                 MesaiDate__month=month,
                 Personel_id__in=personel_ids
             )
             
             if target_type == 'personel' and personel_id:
                 qs = qs.filter(Personel_id=personel_id)
             
             val = None
             if bulk_action == 'all_full': val = Mesai.RISKLI_TAM
             elif bulk_action == 'all_nobet': val = Mesai.RISKLI_NOBET
             elif bulk_action == 'all_clear': val = None
             
             if val is not None or bulk_action == 'all_clear':
                 qs.update(riskli_calisma=val)

        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
