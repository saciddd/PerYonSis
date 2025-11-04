from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from ..models import Personel, PersonelListesiKayit


@login_required
def personel_yonetim(request):
    if not request.user.has_permission('ÇS 657 Personel Yönetimi'):
        return HttpResponseForbidden('Yetkiniz yok.')
    return render(request, 'mercis657/personel_yonetim.html')


@login_required
def personel_sorgula(request):
    if not request.user.has_permission('ÇS 657 Personel Yönetimi'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    ad_soyad = (request.GET.get('ad_soyad') or '').strip()
    tckn = (request.GET.get('tckn') or '').strip()
    donem = (request.GET.get('donem') or '').strip()  # YYYY/MM

    qs = Personel.objects.all().order_by('PersonelName', 'PersonelSurname')
    if ad_soyad:
        # Basit arama: hem ad hem soyad alanlarında küçük/büyük harfe duyarsız arama
        qs = qs.filter(PersonelName__icontains=ad_soyad) | qs.filter(PersonelSurname__icontains=ad_soyad)
    if tckn:
        qs = qs.filter(PersonelTCKN__icontains=tckn)

    results = []
    for p in qs:
        latest_kayit = PersonelListesiKayit.objects.filter(personel=p).order_by('-liste__yil', '-liste__ay').select_related('liste__birim').first()

        latest_info = None
        if latest_kayit:
            latest_info = {
                'yil': latest_kayit.liste.yil,
                'ay': latest_kayit.liste.ay,
                'birim': latest_kayit.liste.birim.BirimAdi,
                'birim_id': latest_kayit.liste.birim.BirimID,
            }

        # Dönem filtresi istendiyse, latest yerine o dönemdeki varlığı kontrol ederek filtreleyelim
        if donem:
            try:
                yil_str, ay_str = donem.split('/')
                yil, ay = int(yil_str), int(ay_str)
                donemde_var_mi = PersonelListesiKayit.objects.filter(personel=p, liste__yil=yil, liste__ay=ay).exists()
                if not donemde_var_mi:
                    continue
            except Exception:
                pass

        results.append({
            'id': p.PersonelID,
            'tckn': str(p.PersonelTCKN),
            'ad_soyad': f"{p.PersonelName} {p.PersonelSurname}",
            'unvan': p.PersonelTitle or '',
            'latest': latest_info,
        })

    return JsonResponse({'status': 'ok', 'data': results})


@login_required
def personel_listeleri(request, personel_id: int):
    if not request.user.has_permission('ÇS 657 Personel Yönetimi'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    personel = get_object_or_404(Personel, pk=personel_id)
    kayitlar = (
        PersonelListesiKayit.objects
        .filter(personel=personel)
        .select_related('liste__birim')
        .order_by('-liste__yil', '-liste__ay')
    )

    data = [
        {
            'yil': k.liste.yil,
            'ay': k.liste.ay,
            'birim': k.liste.birim.BirimAdi,
            'birim_id': k.liste.birim.BirimID,
        }
        for k in kayitlar
    ]

    return JsonResponse(data, safe=False)


