from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Birim, PersonelListesi, PersonelListesiKayit, Personel
from django.db import transaction

@csrf_exempt
@require_POST
@login_required
def personel_kaydet(request):
    import json
    try:
        data = json.loads(request.body)
        donem = data.get('donem')
        birim_id = data.get('birim_id')
        personeller = data.get('personeller', [])
        if not (donem and birim_id and personeller):
            return JsonResponse({'status': 'error', 'message': 'Eksik veri.'})
        year, month = map(int, donem.replace('-', '/').split('/'))
        birim = Birim.objects.get(BirimID=birim_id)
        with transaction.atomic():
            liste, _ = PersonelListesi.objects.get_or_create(birim=birim, yil=year, ay=month)
            eklenenler = []
            for p in personeller:
                pid = p.get('PersonelTCKN')
                pname = p.get('PersonelName')
                psurname = p.get('PersonelSurname')
                ptitle = p.get('PersonelTitle')
                personel, _ = Personel.objects.get_or_create(
                    PersonelTCKN=pid,
                    defaults={'PersonelName': pname, 'PersonelSurname': psurname, 'PersonelTitle': ptitle}
                )
                # Eğer personel varsa, ad/ünvan güncelle
                if personel.PersonelName != pname or personel.PersonelSurname != psurname or personel.PersonelTitle != ptitle:
                    personel.PersonelName = pname
                    personel.PersonelSurname = psurname
                    personel.PersonelTitle = ptitle
                    personel.save()
                # Listeye ekle
                PersonelListesiKayit.objects.get_or_create(liste=liste, personel=personel)
                eklenenler.append(pid)
        return JsonResponse({'status': 'success', 'message': f'{len(eklenenler)} personel eklendi.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# Yeni Personel Ekleme İşlemi
def personel_ekle(request):
    if request.method == 'POST':
        # Form verilerini al
        personel_tc = request.POST['PersonelTCKN']
        personel_name = request.POST['PersonelName']
        personel_surname = request.POST['PersonelSurname']
        personel_title = request.POST['PersonelTitle']
        
        # Yeni personel kaydet
        personel = Personel(
            PersonelTCKN=personel_tc,
            PersonelName=personel_name,
            PersonelSurname=personel_surname,
            PersonelTitle=personel_title
        )
        personel.save()

        # Başarı mesajı ekleyebilirsiniz
        return redirect('mercis657:personeller')  # Personel listesine yönlendir
    return HttpResponse("Geçersiz istek", status=400)
def personel_update(request):
    if request.method == 'POST':
        personel_tc = request.POST.get('tckn')
        personel_name = request.POST.get('name')
        personel_surname = request.POST.get('surname')
        personel_title = request.POST.get('title')

        # Personeli bul
        personel = get_object_or_404(Personel, PersonelTCKN=personel_tc)
        
        # Güncellenen alanlar
        personel.PersonelName = personel_name
        personel.PersonelSurname = personel_surname
        personel.PersonelTitle = personel_title
        personel.save()  # Değişiklikleri kaydet
        
        return JsonResponse({'status': 'success'})  # Başarı mesajı

    return JsonResponse({'status': 'error'})  # Hatalı durum
