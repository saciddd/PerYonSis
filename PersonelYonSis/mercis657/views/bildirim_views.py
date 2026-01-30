from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.template.loader import render_to_string, get_template
import pdfkit
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib import messages
from django.conf import settings
import re
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Bildirim, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from mercis657.utils import hesapla_fazla_mesai, get_turkish_month_name


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
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
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
    
    # Yetki kontrolünü context'e ekle
    can_approve_notifications = request.user.has_permission("ÇS 657 Bildirim Onaylama")
    print ("", can_approve_notifications)
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
def bildirim_onayla(request, bildirim_id):
    """Bildirimi onayla"""
    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if not request.user.has_permission("ÇS 657 Bildirim Onaylama"):
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
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
        return HttpResponseForbidden("Yetkiniz yok.")

    if bildirim.OnayDurumu == 1:
        messages.error(request, "Onaylanmış bildirim silinemez.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")


    bildirim.SilindiMi = True
    bildirim.save()
    messages.success(request, "Bildirim başarıyla silindi.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")

@login_required
def bildirim_listele(request, year, month, birim_id):
    """Return JSON list of bildirim data for given year, month and birim."""
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
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
            
            # Gece değerleri
            gnormal = float(bildirim.GeceNormalFazlaMesai)
            gbayram = float(bildirim.GeceBayramFazlaMesai)
            grnormal = float(bildirim.GeceRiskliNormalFazlaMesai)
            grbayram = float(bildirim.GeceRiskliBayramFazlaMesai)
            
            nicap = float(bildirim.NormalIcap)
            bicap = float(bildirim.BayramIcap)
            mesai_detay = bildirim.MesaiDetay or {}
            icap_detay = bildirim.IcapDetay or {}
            onay_durumu = int(bildirim.OnayDurumu or 0)
            mutemet_kilit = bool(bildirim.MutemetKilit)
        else:
             # Değişkenlerin tanımlı olduğundan emin ol
             gnormal = gbayram = grnormal = grbayram = 0.0

        result.append({
            'personel_id': p.PersonelID,
            'personel_name': p.PersonelName + ' ' + p.PersonelSurname,
            'bildirim_id': bildirim_id,
            'normal_mesai': normal,
            'bayram_mesai': bayram,
            'riskli_normal': rnormal,
            'riskli_bayram': rbayram,
            'gece_normal_mesai': gnormal,
            'gece_bayram_mesai': gbayram,
            'gece_riskli_normal': grnormal,
            'gece_riskli_bayram': grbayram,
            'toplam_mesai': normal + bayram + rnormal + rbayram + gnormal + gbayram + grnormal + grbayram,
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
def bildirim_olustur(request):
    """Create or update a single bildirim for a person (expects JSON).
    Body: { personel_id, birim_id, donem: 'YYYY/MM' }
    Returns bildirim_data suitable for JS updateSingleBildirimRow
    """
    try:
        if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
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
        
        # PersonelListesiKayit'ı bul
        personel_listesi_kayit = liste.kayitlar.filter(personel=personel).first()
        if not personel_listesi_kayit:
            return JsonResponse({'status': 'error', 'message': 'Personel listesi kaydı bulunamadı.'}, status=404)

        # Hesaplama fonksiyonunu çağır
        fazla_mesai_sonuclari = hesapla_fazla_mesai(personel_listesi_kayit, year, month)

        normal = fazla_mesai_sonuclari.get('normal_fazla_mesai', Decimal('0.0'))
        bayram = fazla_mesai_sonuclari.get('bayram_fazla_mesai', Decimal('0.0'))
        
        # Gece Değerleri
        gnormal = fazla_mesai_sonuclari.get('normal_gece_fazla_mesai', Decimal('0.0'))
        gbayram = fazla_mesai_sonuclari.get('bayram_gece_fazla_mesai', Decimal('0.0'))
        
        rnormal = Decimal('0.0')
        rbayram = Decimal('0.0')
        grnormal = Decimal('0.0') # Gece Riskli Normal
        grbayram = Decimal('0.0') # Gece Riskli Bayram
        
        nicap = Decimal('0.0')
        bicap = Decimal('0.0')
        
        # load resmi tatiller
        tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
        # tatil_days = [t.TatilTarihi for t in tatiller if t.TatilTipi == 'TAM'] # Artık buna gerek yok

        for m in mesai_qs:
            key = m.MesaiDate.strftime('%Y-%m-%d')
            if m.Izin:
                mesai_detay[key] = {'izin': m.Izin.ad}
            elif m.MesaiTanim:
                mesai_detay[key] = {'saat': m.MesaiTanim.Saat}

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
                    'GeceNormalFazlaMesai': gnormal,
                    'GeceBayramFazlaMesai': gbayram,
                    'GeceRiskliNormalFazlaMesai': grnormal,
                    'GeceRiskliBayramFazlaMesai': grbayram,
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
                bildirim.GeceNormalFazlaMesai = gnormal
                bildirim.GeceBayramFazlaMesai = gbayram
                bildirim.GeceRiskliNormalFazlaMesai = grnormal
                bildirim.GeceRiskliBayramFazlaMesai = grbayram
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
            'gece_normal_mesai': float(bildirim.GeceNormalFazlaMesai),
            'gece_bayram_mesai': float(bildirim.GeceBayramFazlaMesai),
            'gece_riskli_normal': float(bildirim.GeceRiskliNormalFazlaMesai),
            'gece_riskli_bayram': float(bildirim.GeceRiskliBayramFazlaMesai),
            'toplam_mesai': float(bildirim.NormalFazlaMesai + bildirim.BayramFazlaMesai + bildirim.RiskliNormalFazlaMesai + bildirim.RiskliBayramFazlaMesai + bildirim.GeceNormalFazlaMesai + bildirim.GeceBayramFazlaMesai + bildirim.GeceRiskliNormalFazlaMesai + bildirim.GeceRiskliBayramFazlaMesai),
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
    if not request.user.has_permission('ÇS 657 Bildirim İşlemleri'):
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
        # reuse bildirim_olustur logic by constructing a fake request body
        fake_body = json.dumps({'personel_id': personel.PersonelID, 'birim_id': birim.BirimID, 'donem': f'{year}/{month:02d}'})
        subreq = request
        subreq._body = fake_body.encode('utf-8')
        # call internal function
        resp = bildirim_olustur(subreq)
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
    if not request.user.has_permission('ÇS 657 Bildirim Onaylama'):
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
    if not request.user.has_permission('ÇS 657 Bildirim Onaylama'):
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

@login_required
def bildirim_form(request, birim_id):
    if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
        messages.error(request, "Yetkiniz yok.")
        return HttpResponseForbidden("Yetkiniz yok.")

    # year & month from query params (expected ?year=YYYY&month=M)
    try:
        year = int(request.GET.get('year') or datetime.now().year)
        month = int(request.GET.get('month') or datetime.now().month)
    except Exception:
        year = datetime.now().year
        month = datetime.now().month

    # header/context similar to cizelge_yazdir
    kurum = "Kayseri Devlet Hastanesi"
    dokuman_kodu = "KU.FR.07"
    ay_ismi = get_turkish_month_name(month)
    form_adi = f"{year} Yılı {ay_ismi} Fazla Mesai Bildirim Formu"

    # resolve birim
    birim = Birim.objects.filter(BirimID=birim_id).first() or Birim.objects.filter(id=birim_id).first()
    if not birim:
        return HttpResponse(f"Birim bulunamadı: {birim_id}", status=404)

    # find personel list
    liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()

    # Birim adı
    birim_adi = birim.BirimAdi if hasattr(birim, 'BirimAdi') else getattr(birim, 'name', 'Birim Adı Yok')

    # prepare days and resmi tatil info similar to cizelge_yazdir
    num_days = calendar.monthrange(year, month)[1]
    tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
    resmi_tatil_gunleri = [t.TatilTarihi for t in tatiller]

    days = []
    for day_num in range(1, num_days + 1):
        current_date = date(year, month, day_num)
        is_weekend = current_date.weekday() >= 5
        is_holiday = current_date in resmi_tatil_gunleri
        days.append({
            'day_num': day_num,
            'full_date': current_date.strftime('%Y-%m-%d'),
            'is_weekend': is_weekend,
            'is_holiday': is_holiday,
        })

    personel_rows = []
    if liste:
        kayitlar = liste.kayitlar.select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname')
        for kayit in kayitlar:
            p = kayit.personel
            # get bildirim if exists
            donem_baslangic = date(year, month, 1)
            bildirim = Bildirim.objects.filter(Personel=p, DonemBaslangic=donem_baslangic, SilindiMi=False).first()

            normal = bildirim.NormalFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            gece_normal = bildirim.GeceNormalFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            
            bayram = bildirim.BayramFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            gece_bayram = bildirim.GeceBayramFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            
            rnormal = bildirim.RiskliNormalFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            gece_rnormal = bildirim.GeceRiskliNormalFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            
            rbayram = bildirim.RiskliBayramFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')
            gece_rbayram = bildirim.GeceRiskliBayramFazlaMesai or Decimal('0.0') if bildirim else Decimal('0.0')

            daily_mesai = bildirim.MesaiDetay if (bildirim and bildirim.MesaiDetay) else {}
            onay = int(bildirim.OnayDurumu) if (bildirim and bildirim.OnayDurumu is not None) else 0

            personel_rows.append({
                'sira_no': kayit.sira_no or 0,
                'personel': p,
                'normal_fazla_mesai': normal,
                'gece_normal_fazla_mesai': gece_normal,
                'bayram_fazla_mesai': bayram,
                'gece_bayram_fazla_mesai': gece_bayram,
                'riskli_normal': rnormal,
                'gece_riskli_normal': gece_rnormal,
                'riskli_bayram': rbayram,
                'gece_riskli_bayram': gece_rbayram,
                'toplam': (normal + gece_normal + bayram + gece_bayram + rnormal + gece_rnormal + rbayram + gece_rbayram),
                'daily_mesai': daily_mesai,
                'onay_durumu': onay,
            })

    # Prepare PDF-specific context using the supplied PDF template (bildirim_formu.html)
    try:
        file_url = f"file:///{staticfiles_storage.path('logo/kdh_logo.png')}"
    except Exception:
        file_url = None

    # Prepare personeller list for the PDF template by mapping existing personel_rows
    resmi_tatil_gunleri_nums = []
    arefe_gunleri_nums = []
    try:
        tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
        resmi_tatil_gunleri_nums = [t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM']
        arefe_gunleri_nums = [t.TatilTarihi.day for t in tatiller if t.ArefeMi]
    except Exception:
        pass

    personellers = []
    for row in personel_rows:
        p = row.get('personel')
        daily = row.get('daily_mesai') or {}
        onay_durumu = "Onaylandı" if row.get('onay_durumu', 0) == 1 else "Beklemede"
        mesai_data = []
        for d in days:
            key = d['full_date']
            entry = daily.get(key, {})
            if isinstance(entry, dict):
                saat = entry.get('saat', '')
                izinad = entry.get('izin', '')
                mesai_notu = entry.get('not', '')
            else:
                saat = entry or ''
                izinad = ''
                mesai_notu = ''
            md = {
                'MesaiTanimID': None,
                'Saat': saat,
                'IzinAd': izinad,
                'MesaiNotu': mesai_notu,
                'is_weekend': d.get('is_weekend', False),
                'is_holiday': (d['day_num'] in resmi_tatil_gunleri_nums),
                'is_arife': (d['day_num'] in arefe_gunleri_nums),
            }
            mesai_data.append(md)

        personellers.append({
            'PersonelName': getattr(p, 'PersonelName', ''),
            'PersonelSurname': getattr(p, 'PersonelSurname', ''),
            'PersonelTCKN': getattr(p, 'PersonelTCKN', ''),
            'PersonelTitle': getattr(p, 'PersonelTitle', ''),
            'normal_fazla_mesai': row.get('normal_fazla_mesai'),
            'gece_normal_fazla_mesai': row.get('gece_normal_fazla_mesai'),
            'bayram_fazla_mesai': row.get('bayram_fazla_mesai'),
            'gece_bayram_fazla_mesai': row.get('gece_bayram_fazla_mesai'),
            'riskli_normal': row.get('riskli_normal'),
            'gece_riskli_normal': row.get('gece_riskli_normal'),
            'riskli_bayram': row.get('riskli_bayram'),
            'gece_riskli_bayram': row.get('gece_riskli_bayram'),
            'mesai_data': mesai_data,
            'hesaplama': {'fazla_mesai': None},
            'onay_durumu': onay_durumu,
        })

    # prepare context matching the PDF template
    context_pdf = {
        'kurum': kurum,
        'dokuman_kodu': dokuman_kodu,
        'form_adi': form_adi,
        'yayin_tarihi': 'Haziran 2018',
        'revizyon_tarihi': 'Ekim 2025',
        'revizyon_no': '02',
        'sayfa_no': '1',
        'birim_adi': birim_adi,
        'pdf_logo': file_url,
        'personellers': personellers,
        'personeller': personellers,
        'days': days,
        'resmi_tatil_gunleri': resmi_tatil_gunleri_nums,
        'arefe_gunleri': arefe_gunleri_nums,
        'year': year,
        'month': month,
        'aciklama': liste.aciklama if liste else '',
    }

    # Render PDF template and generate PDF (landscape)
    try:
        template = get_template('mercis657/pdf/bildirim_formu.html')
        html = template.render({**context_pdf})
    except Exception:
        html = render_to_string('mercis657/pdf/bildirim_formu.html', context_pdf)

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': '',
        'enable-external-links': True,
        'quiet': ''
    }

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"bildirim_form_{birim.BirimAdi}_{year}_{month:02d}.pdf"
    filename = filename.replace(' ', '_')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

@login_required
def riskli_bildirim_data(request, birim_id):
    """Riskli bildirim yönetimi için veri sağlar"""
    try:
        if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
            return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

        donem = request.GET.get('donem')
        if not donem:
            return JsonResponse({'status': 'error', 'message': 'Dönem parametresi gerekli.'}, status=400)

        year, month = map(int, donem.split('/') if '/' in donem else donem.split('-'))

        birim = Birim.objects.filter(BirimID=birim_id).first()
        if not birim:
            return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

        liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
        if not liste:
            return JsonResponse({'status': 'error', 'message': 'Personel listesi bulunamadı.'}, status=404)

        bildirimler = []
        for kayit in liste.kayitlar.select_related('personel'):
            bildirim = Bildirim.objects.filter(
                Personel=kayit.personel,
                DonemBaslangic=date(year, month, 1)
            ).first()

            if bildirim:
                bildirimler.append({
                    'bildirim_id': bildirim.BildirimID,
                    'personel_adi': f"{kayit.personel.PersonelName} {kayit.personel.PersonelSurname}",
                    'normal_mesai': float(bildirim.NormalFazlaMesai or 0),
                    'bayram_mesai': float(bildirim.BayramFazlaMesai or 0),
                    'riskli_normal': float(bildirim.RiskliNormalFazlaMesai or 0),
                    'riskli_bayram': float(bildirim.RiskliBayramFazlaMesai or 0),
                    'gece_normal_mesai': float(bildirim.GeceNormalFazlaMesai or 0),
                    'gece_bayram_mesai': float(bildirim.GeceBayramFazlaMesai or 0),
                    'gece_riskli_normal': float(bildirim.GeceRiskliNormalFazlaMesai or 0),
                    'gece_riskli_bayram': float(bildirim.GeceRiskliBayramFazlaMesai or 0),
                })

        return JsonResponse({'status': 'success', 'bildirimler': bildirimler})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def update_risky_bildirim(request, birim_id):
    """Riskli bildirim değerlerini günceller"""
    try:
        if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
            return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

        data = json.loads(request.body)
        changes = data.get('changes', [])

        if not changes:
            return JsonResponse({'status': 'error', 'message': 'Güncellenecek veri bulunamadı.'}, status=400)

        with transaction.atomic():
            not_updated = []
            updated_count = 0
            for change in changes:
                bildirim = Bildirim.objects.filter(BildirimID=change['bildirim_id']).first()
                if not bildirim:
                    continue
                # Eğer bildirim onaylıysa değişiklik yapılmaz, listeye ekle
                if bildirim.OnayDurumu == 1:
                    try:
                        p = bildirim.Personel
                        person_name = f"{p.PersonelName} {p.PersonelSurname}"
                    except Exception:
                        person_name = str(bildirim.BildirimID)
                    not_updated.append(f"Bildirim.{person_name} isimli personelin bildirimi onaylandığı için değişiklik yapılmadı")
                else:
                    bildirim.RiskliNormalFazlaMesai = Decimal(str(change.get('riskli_normal', 0)))
                    bildirim.RiskliBayramFazlaMesai = Decimal(str(change.get('riskli_bayram', 0)))
                    bildirim.NormalFazlaMesai = Decimal(str(change.get('normal_mesai', 0)))
                    bildirim.BayramFazlaMesai = Decimal(str(change.get('bayram_mesai', 0)))
                    
                    # Gece alanları
                    bildirim.GeceRiskliNormalFazlaMesai = Decimal(str(change.get('gece_riskli_normal', 0)))
                    bildirim.GeceRiskliBayramFazlaMesai = Decimal(str(change.get('gece_riskli_bayram', 0)))
                    bildirim.GeceNormalFazlaMesai = Decimal(str(change.get('gece_normal_mesai', 0)))
                    bildirim.GeceBayramFazlaMesai = Decimal(str(change.get('gece_bayram_mesai', 0)))
                    
                    bildirim.save()
                    updated_count += 1

        resp = {'status': 'success', 'message': 'Değişiklikler başarıyla kaydedildi.'}
        resp['updated_count'] = updated_count
        if not_updated:
            resp['not_updated'] = not_updated
        return JsonResponse(resp)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def convert_all_to_risky(request, birim_id):
    """Tüm bildirimleri riskli hale çevirir"""
    try:
        if not request.user.has_permission("ÇS 657 Bildirim İşlemleri"):
            return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

        data = json.loads(request.body)
        donem = data.get('donem')

        if not donem:
            return JsonResponse({'status': 'error', 'message': 'Dönem parametresi gerekli.'}, status=400)

        year, month = map(int, donem.split('/') if '/' in donem else donem.split('-'))

        birim = Birim.objects.filter(BirimID=birim_id).first()
        if not birim:
            return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)

        liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()
        if not liste:
            return JsonResponse({'status': 'error', 'message': 'Personel listesi bulunamadı.'}, status=404)

        with transaction.atomic():
            not_updated = []
            updated_count = 0
            for kayit in liste.kayitlar.select_related('personel'):
                bildirim = Bildirim.objects.filter(
                    Personel=kayit.personel,
                    DonemBaslangic=date(year, month, 1)
                ).first()

                if not bildirim:
                    continue

                if bildirim.OnayDurumu == 1:
                    try:
                        p = kayit.personel
                        person_name = f"{p.PersonelName} {p.PersonelSurname}"
                    except Exception:
                        person_name = str(bildirim.BildirimID)
                    not_updated.append(f"Bildirim.{person_name} isimli personelin bildirimi onaylandığı için değişiklik yapılmadı")
                else:
                    bildirim.RiskliNormalFazlaMesai = bildirim.NormalFazlaMesai
                    bildirim.RiskliBayramFazlaMesai = bildirim.BayramFazlaMesai
                    bildirim.NormalFazlaMesai = Decimal('0.0')
                    bildirim.BayramFazlaMesai = Decimal('0.0')
                    bildirim.save()
                    updated_count += 1

        resp = {'status': 'success', 'message': 'Tüm bildirimler riskli hale çevrildi.'}
        resp['updated_count'] = updated_count
        if not_updated:
            resp['not_updated'] = not_updated
        return JsonResponse(resp)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})