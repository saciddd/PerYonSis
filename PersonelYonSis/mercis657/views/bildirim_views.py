from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Bildirim, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction


def get_donemler():
    """Mevcut aydan -6 ay ile +2 ay arası dönem listesi"""
    today = date.today().replace(day=1)
    donemler = []
    for i in range(-6, 3):
        d = today + relativedelta(months=i)
        value = f"{d.year}/{d.month:02d}"
        label = f"{d.month:02d}/{d.year}" # Görüntülenecek format
        donemler.append({'value': value, 'label': label})
    return donemler


@login_required
def bildirimler(request):
    """Mesai ve İcap bildirimlerini birleşik görüntüler"""
    if not request.user.has_permission("mercis657.view_bildirim"):
        return HttpResponseForbidden("Yetkiniz yok.")

    selected_donem = request.GET.get("donem")
    if not selected_donem:
        today = date.today().replace(day=1)
        selected_donem = f"{today.year}/{today.month:02d}"

    year, month = map(int, selected_donem.split("/"))
    donem_baslangic = date(year, month, 1)

    # Kullanıcının yetkili olduğu birimleri al
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim__BirimID', flat=True)
    birimler = Birim.objects.filter(BirimID__in=user_birimler)

    selected_birim_id = request.GET.get("birim_id")
    if selected_birim_id and int(selected_birim_id) in user_birimler:
        selected_birim = get_object_or_404(Birim, BirimID=selected_birim_id)
    else:
        selected_birim = birimler.first() # Varsayılan olarak ilk birimi seç
    
    personel_data_for_template = []

    if selected_birim:
        # Seçilen döneme ve birime ait PersonelListesi'ni bul
        personel_listesi_obj = PersonelListesi.objects.filter(
            birim=selected_birim, yil=year, ay=month
        ).first()

        if personel_listesi_obj:
            # PersonelListesi'ndeki tüm personelleri al
            personel_kayitlari = PersonelListesiKayit.objects.filter(liste=personel_listesi_obj).select_related('personel')
            personeller_in_list = [pk.personel for pk in personel_kayitlari]

            # Her personel için Bildirim verilerini topla
            for personel in personeller_in_list:
                bildirim = Bildirim.objects.filter(
                    PersonelListesi=personel_listesi_obj,
                    DonemBaslangic=donem_baslangic,
                    SilindiMi=False,
                ).first() # Personel listesi ve dönem başlangıcına göre bildirim
                
                daily_mesai_detay = {}
                daily_icap_detay = {}
                total_normal_fazla_mesai = 0
                total_bayram_fazla_mesai = 0
                total_riskli_normal_fazla_mesai = 0
                total_riskli_bayram_fazla_mesai = 0
                total_normal_icap = 0
                total_bayram_icap = 0
                onay_durumu = 0
                onaylayan_kullanici = None
                onay_tarihi = None
                bildirim_id = None
                calisma_gunleri = 0

                if bildirim:
                    bildirim_id = bildirim.BildirimID
                    onay_durumu = bildirim.OnayDurumu
                    onaylayan_kullanici = bildirim.OnaylayanKullanici
                    onay_tarihi = bildirim.OnayTarihi
                    
                    total_normal_fazla_mesai = bildirim.NormalFazlaMesai
                    total_bayram_fazla_mesai = bildirim.BayramFazlaMesai
                    total_riskli_normal_fazla_mesai = bildirim.RiskliNormalFazlaMesai
                    total_riskli_bayram_fazla_mesai = bildirim.RiskliBayramFazlaMesai
                    total_normal_icap = bildirim.NormalIcap
                    total_bayram_icap = bildirim.BayramIcap

                    if bildirim.MesaiDetay: # JSONField olduğu için kontrol et
                        daily_mesai_detay = {date_str: hours for date_str, hours in bildirim.MesaiDetay.items()}
                    if bildirim.IcapDetay:
                        daily_icap_detay = {date_str: hours for date_str, hours in bildirim.IcapDetay.items()}
                    calisma_gunleri = len(daily_mesai_detay) # Örnek: MesaiDetay dolu gün sayısı

                personel_data_for_template.append({
                    'personel': personel,
                    'bildirim_id': bildirim_id,
                    'normal_fazla_mesai': total_normal_fazla_mesai,
                    'bayram_fazla_mesai': total_bayram_fazla_mesai,
                    'riskli_normal_fazla_mesai': total_riskli_normal_fazla_mesai,
                    'riskli_bayram_fazla_mesai': total_riskli_bayram_fazla_mesai,
                    'toplam_fazla_mesai': total_normal_fazla_mesai + total_bayram_fazla_mesai + 
                                          total_riskli_normal_fazla_mesai + total_riskli_bayram_fazla_mesai,
                    'normal_icap': total_normal_icap,
                    'bayram_icap': total_bayram_icap,
                    'toplam_icap': total_normal_icap + total_bayram_icap,
                    'calisma_gunleri': calisma_gunleri,
                    'onay_durumu': onay_durumu,
                    'onaylayan_kullanici': onaylayan_kullanici,
                    'onay_tarihi': onay_tarihi,
                    'daily_mesai_detay': daily_mesai_detay,
                    'daily_icap_detay': daily_icap_detay,
                })
        
    # Ayın günlerini hazırla
    num_days = calendar.monthrange(year, month)[1]
    days = []
    for day_num in range(1, num_days + 1):
        current_date = date(year, month, day_num)
        is_weekend = current_date.weekday() >= 5  # Cumartesi (5) veya Pazar (6)
        is_holiday = False # ResmiTatil modelinden kontrol edilebilir
        days.append({
            'day_num': day_num,
            'full_date': current_date.strftime("%Y-%m-%d"),
            'is_weekend': is_weekend,
            'is_holiday': is_holiday,
        })

    print(personel_data_for_template)
    # Yetki kontrolünü context'e ekle
    can_approve_notifications = request.user.has_permission("mercis657.change_bildirim")

    context = {
        "donemler": get_donemler(),
        "selected_donem": selected_donem,
        "birimler": birimler,
        "selected_birim": selected_birim,
        "personel_data": personel_data_for_template,
        "days": days,
        "current_month_label": calendar.month_name[month], # Ay adını şablonda göstermek için
        "current_year": year,
        "can_approve_notifications": can_approve_notifications,
    }
    return render(request, "mercis657/bildirimler.html", context)


@login_required
def bildirim_olustur(request, liste_id, donem):
    """Yeni bildirim oluştur"""
    if not request.user.has_permission("mercis657.add_bildirim"):
        return HttpResponseForbidden("Yetkiniz yok.")

    liste = get_object_or_404(PersonelListesi, pk=liste_id)
    year, month = map(int, donem.split("/"))
    donem_baslangic = date(year, month, 1)

    # Eğer bu personel listesi ve dönem için zaten bir bildirim varsa
    existing_bildirim = Bildirim.objects.filter(
        PersonelListesi=liste,
        DonemBaslangic=donem_baslangic,
        SilindiMi=False
    ).first()

    if existing_bildirim:
        if existing_bildirim.OnayDurumu == 1: # Onaylanmışsa hata ver
            messages.error(request, f"Bu dönem için zaten onaylanmış bir bildirim mevcut ve güncellenemez.")
        else: # Onaylanmamışsa güncelle
            # Burada fazla mesai ve icap detaylarını yeniden hesaplayıp güncelleyebilirsiniz.
            # Şimdilik varsayılan değerleri bırakıyorum ya da boş JSON ile güncelliyorum.
            existing_bildirim.OlusturanKullanici = request.user
            existing_bildirim.OnayDurumu = 0
            existing_bildirim.OnaylayanKullanici = None
            existing_bildirim.OnayTarihi = None
            existing_bildirim.MesaiDetay = {}
            existing_bildirim.IcapDetay = {}
            # Diğer fazla mesai/icap alanları sıfırlanabilir veya yeniden hesaplanabilir
            existing_bildirim.NormalFazlaMesai = 0
            existing_bildirim.BayramFazlaMesai = 0
            existing_bildirim.RiskliNormalFazlaMesai = 0
            existing_bildirim.RiskliBayramFazlaMesai = 0
            existing_bildirim.NormalIcap = 0
            existing_bildirim.BayramIcap = 0

            existing_bildirim.save()
            messages.info(request, f"Mevcut onaylanmamış bildirim güncellendi.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={donem}&birim_id={liste.birim.BirimID}")

    # Yeni bildirim oluştur
    bildirim = Bildirim.objects.create(
        PersonelListesi=liste,
        DonemBaslangic=donem_baslangic,
        OlusturanKullanici=request.user,
        OnayDurumu=0,  # Oluşturulduğunda beklemede
        SilindiMi=False,
        MesaiDetay={},
        IcapDetay={},
        NormalFazlaMesai=0,
        BayramFazlaMesai=0,
        RiskliNormalFazlaMesai=0,
        RiskliBayramFazlaMesai=0,
        NormalIcap=0,
        BayramIcap=0,
    )
    messages.success(request, f"Bildirim başarıyla oluşturuldu.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={donem}&birim_id={liste.birim.BirimID}")


@login_required
def bildirim_onayla(request, bildirim_id):
    """Bildirimi onayla"""
    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if not request.user.has_permission("mercis657.change_bildirim"):
        return HttpResponseForbidden("Yetkiniz yok.")

    if bildirim.OnayDurumu == 1:
        messages.warning(request, "Bildirim zaten onaylanmış.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")

    bildirim.OnayDurumu = 1
    bildirim.OnaylayanKullanici = request.user
    bildirim.OnayTarihi = date.today() # datetime.now() olarak güncellenebilir
    bildirim.save()

    messages.success(request, "Bildirim başarıyla onaylandı.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")


@login_required
def bildirim_sil(request, bildirim_id):
    """Bildirimi soft delete yap"""
    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if not request.user.has_permission("mercis657.delete_bildirim"):
        return HttpResponseForbidden("Yetkiniz yok.")

    if bildirim.OnayDurumu == 1:
        messages.error(request, "Onaylanmış bildirim silinemez.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")


    bildirim.SilindiMi = True
    bildirim.save()
    messages.success(request, "Bildirim başarıyla silindi.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")

@login_required
def bildirim_toplu_olustur(request, birim_id):
    pass

@login_required
def bildirim_toplu_onay(request, birim_id):
    pass

@login_required
def bildirim_tekil_onay(request, bildirim_id):
    pass

@login_required
def bildirim_toplu_onay_kaldir(request, birim_id):
    pass

@login_required
def bildirim_form(request, birim_id):
    pass

@login_required
def bildirim_kilit(request, bildirim_id):
    pass

@login_required
def bildirim_kilit_ac(request, bildirim_id):
    pass

@login_required
def toplu_kilit(request):
    pass

@login_required
def resmi_tatiller(request):
    pass

@login_required
def bildirim_excel(request):
    pass

@login_required
def tatil_ekle(request):
    pass

@login_required
def tatil_duzenle(request):
    pass

@login_required
def tatil_sil(request, tatil_id):
    pass

@login_required
def cizelge_form(request, birim_id):
    pass

@login_required
def bildirim_listele(request, year, month, birim_id):
    """Return JSON list of bildirim data for given year, month and birim."""
    if not request.user.has_permission("mercis657.view_bildirim"):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    try:
        year = int(year); month = int(month)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz tarih.'}, status=400)

    birim = Birim.objects.filter(BirimID=birim_id).first()
    if not birim:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
    if not liste:
        return JsonResponse({'status': 'success', 'data': []})

    donem_baslangic = date(year, month, 1)
    result = []

    # preload Mesai and ResmiTatil
    from ..models import ResmiTatil as RT
    tatiller = RT.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
    tatil_days = [t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM']

    personel_kayitlari = liste.kayitlar.select_related('personel').all()
    for kayit in personel_kayitlari:
        p = kayit.personel
        bildirim = Bildirim.objects.filter(Personel=p, DonemBaslangic=donem_baslangic, SilindiMi=False).first()

        # defaults
        normal = bayram = rnormal = rbayram = nicap = bicap = 0
        mesai_detay = {}
        icap_detay = {}
        onay_durumu = 0
        mutemet_kilit = False
        bildirim_id = None

        if bildirim:
            bildirim_id = bildirim.BildirimID
            normal = float(bildirim.NormalFazlaMesai)
            bayram = float(bildirim.BayramFazlaMesai)
            rnormal = float(bildirim.RiskliNormalFazlaMesai)
            rbayram = float(bildirim.RiskliBayramFazlaMesai)
            nicap = float(bildirim.NormalIcap)
            bicap = float(bildirim.BayramIcap)
            mesai_detay = bildirim.MesaiDetay or {}
            icap_detay = bildirim.IcapDetay or {}
            onay_durumu = int(bildirim.OnayDurumu or 0)
            mutemet_kilit = bool(bildirim.MutemetKilit)

        result.append({
            'personel_id': p.PersonelID,
            'personel_name': p.PersonelName,
            'bildirim_id': bildirim_id,
            'normal_mesai': normal,
            'bayram_mesai': bayram,
            'riskli_normal': rnormal,
            'riskli_bayram': rbayram,
            'toplam_mesai': normal + bayram + rnormal + rbayram,
            'normal_icap': nicap,
            'bayram_icap': bicap,
            'toplam_icap': nicap + bicap,
            'MesaiDetay': mesai_detay,
            'IcapDetay': icap_detay,
            'onay_durumu': onay_durumu,
            'mutemet_kilit': mutemet_kilit,
        })

    return JsonResponse({'status': 'success', 'data': result})


@login_required
@require_POST
def api_bildirim_olustur(request):
    """Create or update a single bildirim for a person (expects JSON).
    Body: { personel_id, birim_id, donem: 'YYYY/MM' }
    Returns bildirim_data suitable for JS updateSingleBildirimRow
    """
    try:
        if not request.user.has_permission("mercis657.add_bildirim"):
            return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

        try:
            data = json.loads(request.body)
            personel_id = int(data.get('personel_id'))
            birim_id = int(data.get('birim_id'))
            donem = data.get('donem')
            if not (personel_id and birim_id and donem):
                return JsonResponse({'status': 'error', 'message': 'Eksik parametre.'}, status=400)
            year, month = map(int, donem.split('/') if '/' in donem else donem.split('-'))
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'}, status=400)

        birim = Birim.objects.filter(BirimID=birim_id).first()
        if not birim:
            return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

        liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
        if not liste:
            return JsonResponse({'status': 'error', 'message': 'Personel listesi bulunamadı.'}, status=404)

        personel = Personel.objects.filter(PersonelID=personel_id).first()
        if not personel:
            return JsonResponse({'status': 'error', 'message': 'Personel bulunamadı.'}, status=404)

        donem_baslangic = date(year, month, 1)

        # Build MesaiDetay and IcapDetay from Mesai entries
        mesai_qs = Mesai.objects.filter(Personel=personel, MesaiDate__year=year, MesaiDate__month=month).select_related('MesaiTanim', 'Izin')
        mesai_detay = {}
        icap_detay = {}
        normal = bayram = rnormal = rbayram = nicap = bicap = 0

        # load resmi tatiller
        tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
        tatil_days = [t.TatilTarihi for t in tatiller if t.TatilTipi == 'TAM']

        for m in mesai_qs:
            key = m.MesaiDate.strftime('%Y-%m-%d')
            if m.Izin:
                mesai_detay[key] = {'izin': m.Izin.ad}
            elif m.MesaiTanim:
                # ensure Mesai_Tanimlari has Sure calculated (could be duration)
                sure_val = 0
                try:
                    sure_val = float(getattr(m.MesaiTanim, 'Sure', 0) or 0)
                except Exception:
                    sure_val = 0
                mesai_detay[key] = {'sure': sure_val, 'saat': m.MesaiTanim.Saat}

            # classify into normal/bayram/risky etc. (basic heuristics)
            is_bayram = m.MesaiDate in tatil_days
            is_risky = bool(getattr(m.MesaiTanim, 'GeceMesaisi', False)) if m.MesaiTanim else False
            sure_hours = 0
            try:
                sure_hours = float(getattr(m.MesaiTanim, 'Sure', 0) or 0)
            except Exception:
                sure_hours = 0

            if is_bayram and is_risky:
                rbayram += sure_hours
            elif is_bayram:
                bayram += sure_hours
            elif is_risky:
                rnormal += sure_hours
            else:
                normal += sure_hours

        # Create or update Bildirim
        with transaction.atomic():
            bildirim, created = Bildirim.objects.get_or_create(
                Personel=personel,
                DonemBaslangic=donem_baslangic,
                defaults={
                    'PersonelListesi': liste,
                    'OlusturanKullanici': request.user,
                    'MesaiDetay': mesai_detay,
                    'IcapDetay': icap_detay,
                    'NormalFazlaMesai': normal,
                    'BayramFazlaMesai': bayram,
                    'RiskliNormalFazlaMesai': rnormal,
                    'RiskliBayramFazlaMesai': rbayram,
                    'NormalIcap': nicap,
                    'BayramIcap': bicap,
                }
            )
            if not created:
                # if exists and not approved, update
                if bildirim.OnayDurumu == 1:
                    return JsonResponse({'status': 'error', 'message': 'Bildirim zaten onaylanmış, güncellenemez.'}, status=400)
                bildirim.MesaiDetay = mesai_detay
                bildirim.IcapDetay = icap_detay
                bildirim.NormalFazlaMesai = normal
                bildirim.BayramFazlaMesai = bayram
                bildirim.RiskliNormalFazlaMesai = rnormal
                bildirim.RiskliBayramFazlaMesai = rbayram
                bildirim.NormalIcap = nicap
                bildirim.BayramIcap = bicap
                bildirim.OlusturanKullanici = request.user
                bildirim.save()

        bildirim_data = {
            'personel_id': personel.PersonelID,
            'bildirim_id': bildirim.BildirimID,
            'normal_mesai': float(bildirim.NormalFazlaMesai),
            'bayram_mesai': float(bildirim.BayramFazlaMesai),
            'riskli_normal': float(bildirim.RiskliNormalFazlaMesai),
            'riskli_bayram': float(bildirim.RiskliBayramFazlaMesai),
            'toplam_mesai': float(bildirim.ToplamFazlaMesai),
            'normal_icap': float(bildirim.NormalIcap),
            'bayram_icap': float(bildirim.BayramIcap),
            'toplam_icap': float(bildirim.ToplamIcap),
            'MesaiDetay': bildirim.MesaiDetay or {},
            'IcapDetay': bildirim.IcapDetay or {},
            'onay_durumu': int(bildirim.OnayDurumu or 0),
            'mutemet_kilit': bool(bildirim.MutemetKilit),
        }

        return JsonResponse({'status': 'success', 'bildirim_data': bildirim_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def bildirim_toplu_olustur(request, birim_id):
    if not request.user.has_permission('mercis657.add_bildirim'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    try:
        data = json.loads(request.body)
        year = int(data.get('year'))
        month = int(data.get('month'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz parametre.'}, status=400)

    birim = Birim.objects.filter(BirimID=birim_id).first()
    if not birim:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
    if not liste:
        return JsonResponse({'status': 'error', 'message': 'Personel listesi yok.'}, status=404)

    donem_baslangic = date(year, month, 1)
    count = 0
    for kayit in liste.kayitlar.select_related('personel'):
        personel = kayit.personel
        # reuse api_bildirim_olustur logic by constructing a fake request body
        fake_body = json.dumps({'personel_id': personel.PersonelID, 'birim_id': birim.BirimID, 'donem': f'{year}/{month:02d}'})
        subreq = request
        subreq._body = fake_body.encode('utf-8')
        # call internal function
        resp = api_bildirim_olustur(subreq)
        try:
            rdata = json.loads(resp.content)
            if rdata.get('status') == 'success':
                count += 1
        except Exception:
            continue

    return JsonResponse({'status': 'success', 'message': f'{count} bildirim oluşturuldu/güncellendi.', 'count': count})


@login_required
@require_POST
def bildirim_tekil_onay(request, bildirim_id):
    if not request.user.has_permission('mercis657.change_bildirim'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    try:
        data = json.loads(request.body)
        onay = int(data.get('onay_durumu'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz parametre.'}, status=400)

    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if bildirim.MutemetKilit:
        return JsonResponse({'status': 'error', 'message': 'Bu bildirim kilitli.'}, status=400)

    if onay == 1:
        bildirim.OnayDurumu = 1
        bildirim.OnaylayanKullanici = request.user
        bildirim.OnayTarihi = timezone.now()
        bildirim.save()
        message = 'Bildirim onaylandı.'
    else:
        bildirim.OnayDurumu = 0
        bildirim.OnaylayanKullanici = None
        bildirim.OnayTarihi = None
        bildirim.save()
        message = 'Bildirim onayı kaldırıldı.'

    bildirim_data = {
        'personel_id': bildirim.Personel.PersonelID,
        'bildirim_id': bildirim.BildirimID,
        'normal_mesai': float(bildirim.NormalFazlaMesai),
        'bayram_mesai': float(bildirim.BayramFazlaMesai),
        'riskli_normal': float(bildirim.RiskliNormalFazlaMesai),
        'riskli_bayram': float(bildirim.RiskliBayramFazlaMesai),
        'toplam_mesai': float(bildirim.ToplamFazlaMesai),
        'normal_icap': float(bildirim.NormalIcap),
        'bayram_icap': float(bildirim.BayramIcap),
        'toplam_icap': float(bildirim.ToplamIcap),
        'MesaiDetay': bildirim.MesaiDetay or {},
        'IcapDetay': bildirim.IcapDetay or {},
        'onay_durumu': int(bildirim.OnayDurumu or 0),
        'mutemet_kilit': bool(bildirim.MutemetKilit),
    }

    return JsonResponse({'status': 'success', 'message': message, 'bildirim_data': bildirim_data})


@login_required
@require_POST
def bildirim_toplu_onay(request, birim_id):
    if not request.user.has_permission('mercis657.change_bildirim'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    try:
        data = json.loads(request.body)
        year = int(data.get('year'))
        month = int(data.get('month'))
        onay = int(data.get('onay_durumu'))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz parametre.'}, status=400)

    birim = Birim.objects.filter(BirimID=birim_id).first()
    if not birim:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
    if not liste:
        return JsonResponse({'status': 'error', 'message': 'Personel listesi yok.'}, status=404)

    donem_baslangic = date(year, month, 1)
    qs = Bildirim.objects.filter(PersonelListesi=liste, DonemBaslangic=donem_baslangic, SilindiMi=False, MutemetKilit=False)
    count = 0
    for b in qs:
        if onay == 1:
            b.OnayDurumu = 1
            b.OnaylayanKullanici = request.user
            b.OnayTarihi = timezone.now()
        else:
            b.OnayDurumu = 0
            b.OnaylayanKullanici = None
            b.OnayTarihi = None
        b.save()
        count += 1

    return JsonResponse({'status': 'success', 'message': f'{count} bildirim güncellendi.', 'count': count})
