from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json
from django.shortcuts import render
from ..models import Mesai, PersonelListesiKayit, MesaiYedek, Mesai_Tanimlari, Izin, UstBirim

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

                mesai_changed = existing_mesai.MesaiTanim_id != mesai_tanim_id
                izin_changed = existing_mesai.Izin_id != izin_id

                if not (mesai_changed or izin_changed):
                    continue

                # Eğer zaten bekleyen değişiklik varken, gelen değer yedekle aynı ise vazgeçilmiş say
                last_backup = existing_mesai.yedekler.order_by('-created_at').first()
                if existing_mesai.Degisiklik and last_backup and \
                   last_backup.MesaiTanim_id == mesai_tanim_id and last_backup.Izin_id == izin_id:
                    existing_mesai.MesaiTanim_id = mesai_tanim_id
                    existing_mesai.Izin_id = izin_id
                    existing_mesai.OnayDurumu = True
                    existing_mesai.Degisiklik = False
                    existing_mesai.save()
                    last_backup.delete()
                    continue

                # Onaylı kayıtta değişiklik -> yedekle ve beklemeye al
                if existing_mesai.OnayDurumu:
                    MesaiYedek.objects.create(
                        mesai=existing_mesai,
                        MesaiTanim_id=existing_mesai.MesaiTanim_id,
                        Izin_id=existing_mesai.Izin_id,
                        created_by=request.user
                    )

                existing_mesai.MesaiTanim_id = mesai_tanim_id
                existing_mesai.Izin_id = izin_id
                existing_mesai.OnayDurumu = False
                existing_mesai.Degisiklik = True
                existing_mesai.save()

            except Mesai.DoesNotExist:
                # Yeni kayıt: onaylı ve değişiklik yok
                Mesai.objects.create(
                    Personel_id=personel_id,
                    MesaiDate=mesai_date,
                    MesaiTanim_id=mesai_tanim_id,
                    Izin_id=izin_id,
                    OnayDurumu=True,
                    Degisiklik=False
                )

        if errors:
            return JsonResponse({'status': 'partial', 'errors': errors})
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'failed'}, status=400)


@login_required
def cizelge_onay(request):
    from datetime import date
    today = date.today()
    default_year = today.year
    default_month = today.month
    year = int(request.GET.get('year', default_year) or default_year)
    month = int(request.GET.get('month', default_month) or default_month)
    ust_birim_id = request.GET.get('ust_birim')

    from ..models import PersonelListesi

    pending_qs = Mesai.objects.filter(OnayDurumu=False, Degisiklik=True)
    if year and month:
        pending_qs = pending_qs.filter(MesaiDate__year=year, MesaiDate__month=month)

    personel_listeleri = PersonelListesi.objects.all()
    if year and month:
        personel_listeleri = personel_listeleri.filter(yil=year, ay=month)
    if ust_birim_id:
        personel_listeleri = personel_listeleri.filter(birim__UstBirim_id=ust_birim_id)

    cards = []
    for liste in personel_listeleri.select_related('birim'):
        person_ids = list(liste.kayitlar.values_list('personel_id', flat=True))
        cnt = pending_qs.filter(Personel_id__in=person_ids).count()
        if cnt:
            cards.append({'birim': liste.birim, 'yil': liste.yil, 'ay': liste.ay, 'count': cnt})

    # Filtre seçenekleri: yıl (geçen, bu, gelecek), ay (1-12), üst birimler
    years = [year-1, year, year+1]
    months = [{'value': i, 'label': i} for i in range(1,13)]
    ust_birimler = UstBirim.objects.all()

    return render(request, 'mercis657/cizelge_onay.html', {
        'cards': cards,
        'year': year,
        'month': month,
        'ust_birim_id': int(ust_birim_id) if (ust_birim_id and ust_birim_id.isdigit()) else '',
        'years': years,
        'months': months,
        'ust_birimler': ust_birimler,
    })


@login_required
def mesai_onayla(request, mesai_id):
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    mesai = Mesai.objects.filter(pk=mesai_id).first()
    if not mesai:
        return JsonResponse({'status': 'error', 'message': 'Kayıt bulunamadı.'}, status=404)
    mesai.OnayDurumu = True
    mesai.Degisiklik = False
    mesai.save()
    mesai.yedekler.all().delete()
    return JsonResponse({'status': 'success'})


@login_required
def mesai_reddet(request, mesai_id):
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    mesai = Mesai.objects.filter(pk=mesai_id).first()
    if not mesai:
        return JsonResponse({'status': 'error', 'message': 'Kayıt bulunamadı.'}, status=404)
    backup = mesai.yedekler.order_by('-created_at').first()
    if not backup:
        return JsonResponse({'status': 'error', 'message': 'Yedek bulunamadı.'}, status=400)
    mesai.MesaiTanim = backup.MesaiTanim
    mesai.Izin = backup.Izin
    mesai.OnayDurumu = True
    mesai.Degisiklik = False
    mesai.save()
    mesai.yedekler.all().delete()
    return JsonResponse({'status': 'success'})


@login_required
def toplu_onay(request, birim_id, year, month):
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    year = int(year)
    month = int(month)
    from ..models import PersonelListesi
    try:
        liste = PersonelListesi.objects.get(birim_id=birim_id, yil=year, ay=month)
    except PersonelListesi.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Personel listesi yok.'}, status=404)
    person_ids = list(liste.kayitlar.values_list('personel_id', flat=True))
    qs = Mesai.objects.filter(Personel_id__in=person_ids, MesaiDate__year=year, MesaiDate__month=month, OnayDurumu=False, Degisiklik=True)
    count = qs.count()
    for m in qs:
        m.OnayDurumu = True
        m.Degisiklik = False
        m.save()
        m.yedekler.all().delete()
    return JsonResponse({'status': 'success', 'count': count})

