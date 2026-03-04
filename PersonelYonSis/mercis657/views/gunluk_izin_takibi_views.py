import os
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from ..models import Kurum, UstBirim, Idareci, Bina, Mesai, PersonelListesiKayit
import json
from datetime import datetime

@login_required
def gunluk_izin_takibi(request):
    """
    Günlük İzin Takibi sayfası.
    """
    sync_file_path = os.path.join(settings.BASE_DIR, 'mercis657', 'last_izin_sync.json')
    last_sync = None
    if os.path.exists(sync_file_path):
        try:
            with open(sync_file_path, 'r', encoding='utf-8') as f:
                last_sync = json.load(f)
        except Exception:
            pass

    context = {
        'kurumlar': Kurum.objects.filter(aktif=True),
        'ust_birimler': UstBirim.objects.filter(aktif=True),
        'idareciler': Idareci.objects.filter(aktif=True),
        'binalar': Bina.objects.filter(aktif=True),
        'bugun': datetime.now().strftime('%Y-%m-%d'),
        'last_sync': last_sync,
    }
    return render(request, 'mercis657/gunluk_izin_takibi.html', context)

@login_required
@require_POST
def gunluk_izin_takibi_search(request):
    """
    AJAX endpoint: Filtrelere göre İzinli Mesai kayıtlarını sorgular.
    JSON input: {kurum_id, ust_birim_id, idareci_id, bina_id, tarih}
    """
    try:
        data = json.loads(request.body)
        kurum_id = data.get('kurum_id')
        ust_birim_id = data.get('ust_birim_id')
        idareci_id = data.get('idareci_id')
        bina_id = data.get('bina_id')
        tarih = data.get('tarih')

        # İzinli olanları getir (Izin_id is not null)
        mesai_qs = Mesai.objects.filter(
            MesaiDate=tarih,
            Izin__isnull=False
        ).select_related(
            'Personel', 
            'Izin'
        )

        kayit_qs = PersonelListesiKayit.objects.filter(
            liste__yil=int(tarih.split('-')[0]),
            liste__ay=int(tarih.split('-')[1])
        ).select_related('liste__birim', 'personel')

        if kurum_id:
            kayit_qs = kayit_qs.filter(liste__birim__Kurum_id=kurum_id)
        if ust_birim_id:
            kayit_qs = kayit_qs.filter(liste__birim__UstBirim_id=ust_birim_id)
        if idareci_id:
            kayit_qs = kayit_qs.filter(liste__birim__Idareci_id=idareci_id)
        if bina_id:
            kayit_qs = kayit_qs.filter(liste__birim__Bina_id=bina_id)

        personel_ids = kayit_qs.values_list('personel_id', flat=True)
        mesai_qs = mesai_qs.filter(Personel_id__in=personel_ids)
        
        personel_birim_map = {}
        for kayit in kayit_qs:
            birim = kayit.liste.birim
            personel_birim_map[kayit.personel_id] = {
                'birim': birim.BirimAdi,
                'unvan': kayit.personel.PersonelTitle or ""
            }

        results = []
        for mesai in mesai_qs:
            p_info = personel_birim_map.get(mesai.Personel_id)
            if not p_info:
                continue 

            results.append({
                'birim': p_info['birim'],
                'personel_ad': f"{mesai.Personel.PersonelName} {mesai.Personel.PersonelSurname}",
                'unvan': p_info['unvan'],
                'sisteme_girildi': mesai.SistemdekiIzin,
                'izin_ad': mesai.Izin.ad if mesai.Izin else ""
            })

        # Sıralama: önce birim, sonra personel
        results.sort(key=lambda x: (x['birim'], x['personel_ad']))

        return JsonResponse({'status': 'success', 'results': results})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
