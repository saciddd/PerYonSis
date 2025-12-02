# mercis657/views/ilk_liste_views.py
import calendar
from datetime import date
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..models import IlkListe, PersonelListesi, PersonelListesiKayit, Mesai, Personel, ResmiTatil
from ..utils import hesapla_fazla_mesai

@login_required
def ilk_liste_olustur(request, liste_id):
    try:
        liste = PersonelListesi.objects.get(pk=liste_id)
    except PersonelListesi.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Liste bulunamadı.'}, status=404)

    # Daha önce bu liste için oluşturulmuş ve onaylanmış bir ilk liste varsa engelle
    if IlkListe.objects.filter(PersonelListesi=liste, OnayDurumu=True).exists():
        return JsonResponse({'status': 'error', 'message': 'Bu liste için zaten ilk bildirim oluşturulmuş.'}, status=400)

    # Tüm personel kayıtlarını çek
    kayitlar = PersonelListesiKayit.objects.filter(liste=liste)
    veriler = []

    for kayit in kayitlar:
        mesailer = Mesai.objects.filter(
            Personel=kayit.personel,
            MesaiDate__year=liste.yil,
            MesaiDate__month=liste.ay
        )

        mesai_data = {}
        for m in mesailer:
            tarih = m.MesaiDate.strftime("%Y-%m-%d")
            if m.Izin:
                mesai_data[tarih] = {"izin": str(m.Izin)}
            elif m.MesaiTanim:
                mesai_data[tarih] = {"saat": str(m.MesaiTanim.Saat)}

        # Fazla mesai örneği (hesaplama fonksiyonundan alınabilir)
        fazla_mesai = hesapla_fazla_mesai(kayit, liste.yil, liste.ay)

        veriler.append({
            "personel": kayit.personel.PersonelID,
            "radyasyon_calisani": kayit.radyasyon_calisani,
            "mesai_data": mesai_data,
            "fazla_mesai": float(fazla_mesai.get('fazla_mesai') or 0),
        })

    ilk_liste = IlkListe.objects.create(
        PersonelListesi=liste,
        Veriler=veriler,
        OlusturanKullanici=request.user
    )

    return JsonResponse({
        'status': 'success',
        'message': 'İlk liste bildirimi oluşturuldu.',
        'ilk_liste_id': ilk_liste.id
    })

@login_required
def ilk_liste_detay(request, liste_id):
    ilk_liste = IlkListe.objects.filter(PersonelListesi_id=liste_id).order_by('-OlusturmaTarihi').first()
    if not ilk_liste:
        return JsonResponse({'status': 'error', 'message': 'Bu listeye ait ilk bildirim bulunamadı.'})

    yil = ilk_liste.PersonelListesi.yil
    ay = ilk_liste.PersonelListesi.ay

    # 🔹 Resmi tatil günleri
    resmi_tatiller = list(
        ResmiTatil.objects.filter(
            TatilTarihi__year=yil,
            TatilTarihi__month=ay
        ).values_list('TatilTarihi', flat=True)
    )
    resmi_tatiller_str = [t.strftime('%Y-%m-%d') for t in resmi_tatiller]

    # 🔹 Gün listesi
    days_in_month = calendar.monthrange(yil, ay)[1]
    days = [
        {
            'full_date': f"{yil}-{ay:02}-{gun:02}",
            'day_num': gun,
            'is_weekend': calendar.weekday(yil, ay, gun) >= 5,
            'is_resmi_tatil': f"{yil}-{ay:02}-{gun:02}" in resmi_tatiller_str
        }
        for gun in range(1, days_in_month + 1)
    ]

    veriler = []
    for v in ilk_liste.Veriler or []:
        try:
            p = Personel.objects.get(pk=v["personel"])
            v["personel_adi"] = f"{p.PersonelName} {p.PersonelSurname}"
        except Personel.DoesNotExist:
            v["personel_adi"] = f"ID {v['personel']} (Kayıt Yok)"
        veriler.append(v)

    onay_yetkisi = request.user.has_permission('ÇS 657 İlk Liste Bildirimi Onaylama')
    data = {
        "status": "success",
        "id": ilk_liste.id,
        "liste": f"{ilk_liste.PersonelListesi.birim} - {ilk_liste.PersonelListesi.yil}/{ilk_liste.PersonelListesi.ay}",
        "olusturan": ilk_liste.OlusturanKullanici.FullName if ilk_liste.OlusturanKullanici else "—",
        "olusturma_tarihi": ilk_liste.OlusturmaTarihi.strftime("%d.%m.%Y %H:%M"),
        "onay_durumu": ilk_liste.OnayDurumu,
        "veriler": veriler,
        "days": days,
        "onay_yetkisi": onay_yetkisi,
    }
    return JsonResponse(data)

@login_required
def ilk_liste_onayla(request, ilk_liste_id):
    try:
        ilk_liste = IlkListe.objects.get(pk=ilk_liste_id)
    except IlkListe.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'İlk liste bildirimi bulunamadı.'}, status=404)

    if not request.user.has_permission('ÇS 657 İlk Liste Bildirimi Onaylama'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    ilk_liste.onayla(request.user)
    return JsonResponse({'status': 'success', 'message': 'İlk liste bildirimi onaylandı.'})

@login_required
def ilk_liste_onay_kaldir(request, ilk_liste_id):
    try:
        ilk_liste = IlkListe.objects.get(pk=ilk_liste_id)
    except IlkListe.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'İlk liste bildirimi bulunamadı.'}, status=404)

    if not request.user.has_permission('ÇS 657 İlk Liste Bildirimi Onaylama'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    ilk_liste.onay_kaldir(request.user)
    return JsonResponse({'status': 'success', 'message': 'İlk liste bildirimi onayı kaldırıldı.'})
