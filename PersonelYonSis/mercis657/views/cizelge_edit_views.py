from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime
import json
from django.shortcuts import get_object_or_404, render
from django.template.loader import get_template
from django.conf import settings
from pathlib import Path
from ..models import Mesai, Personel, PersonelListesi, PersonelListesiKayit, MesaiYedek, Mesai_Tanimlari, Izin, ResmiTatil, UstBirim
from ..utils import hesapla_fazla_mesai
import pdfkit
# PDFKit yapılandırması
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

@login_required
def cizelge_yazdir(request):
    # Çalışma listesi yazdırma sayfası

    # Parse query params: donem=YYYY/MM or year & month; birim_id
    donem = request.GET.get('donem') or request.GET.get('donem')
    birim_id = request.GET.get('birim_id') or request.GET.get('birim')

    # default header variables
    kurum = "Kayseri Devlet Hastanesi"
    dokuman_kodu = "FR-SA-11"

    # Build an absolute file:// path to the logo if STATIC_ROOT is set
    pdf_logo = None
    try:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root:
            logo_path = Path(static_root) / 'logo' / 'kdh_logo.png'
            if logo_path.exists():
                pdf_logo = f"file://{logo_path.as_posix()}"
    except Exception:
        pdf_logo = None

    # Determine year/month
    year = None
    month = None
    if donem:
        try:
            parts = donem.split('/')
            if len(parts) >= 2:
                year = int(parts[0])
                month = int(parts[1])
        except Exception:
            year = None
            month = None
    # fallback to separate params
    if not year or not month:
        try:
            year = int(request.GET.get('year') or datetime.now().year)
            month = int(request.GET.get('month') or datetime.now().month)
        except Exception:
            year = datetime.now().year
            month = datetime.now().month

    # Prepare default empty context pieces
    days = []
    personeller_for_pdf = []
    resmi_tatil_gunleri = []
    arefe_gunleri = []

    try:
        import calendar
        # Resolve birim: Birim may use BirimID field
        from ..models import Birim as _Birim
        birim = None
        if birim_id:
            try:
                birim = _Birim.objects.filter(BirimID=birim_id).first() or _Birim.objects.filter(id=birim_id).first()
            except Exception:
                birim = None

        # Find the personel list for that birim and period
        liste = None
        if birim:
            liste = PersonelListesi.objects.filter(birim=birim, yil=year, ay=month).first()

        # Build days for month
        days_in_month = calendar.monthrange(year, month)[1]
        for d in range(1, days_in_month + 1):
            dow = calendar.weekday(year, month, d)  # 0 Mon .. 6 Sun
            is_weekend = dow >= 5
            days.append({'day_num': d, 'is_weekend': is_weekend})

        # Load resmi tatil list for month
        tatiller = ResmiTatil.objects.filter(TatilTarihi__year=year, TatilTarihi__month=month)
        resmi_tatil_gunleri = [t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM']
        arefe_gunleri = [t.TatilTarihi.day for t in tatiller if t.ArefeMi]

        # If list exists, build person rows
        if liste:
            # iterate over kayitlar to preserve ordering
            for kayit in liste.kayitlar.select_related('personel').all():
                p = kayit.personel
                # build mesai_data aligned with days
                mesai_data = []
                for d in days:
                    day_no = d['day_num']
                    from datetime import date
                    current_date = date(year, month, day_no)
                    mesai = Mesai.objects.filter(Personel=p, MesaiDate=current_date).select_related('MesaiTanim', 'Izin').first()
                    md = {
                        'MesaiTanimID': mesai.MesaiTanim_id if mesai else None,
                        'Saat': (mesai.MesaiTanim.Saat if (mesai and getattr(mesai, 'MesaiTanim', None)) else ''),
                        'IzinAd': (mesai.Izin.ad if (mesai and getattr(mesai, 'Izin', None)) else ''),
                        'is_weekend': d['is_weekend'],
                        'is_holiday': (day_no in resmi_tatil_gunleri),
                        'is_arife': (day_no in arefe_gunleri),
                    }
                    mesai_data.append(md)
                
                #  Fazla mesai hesapla
                hesaplama = hesapla_fazla_mesai(kayit, year, month)

                personeller_for_pdf.append({
                    'PersonelName': p.PersonelName,
                    'PersonelTitle': getattr(p, 'PersonelTitle', ''),
                    'mesai_data': mesai_data,
                    'hesaplama': {'fazla_mesai': hesaplama['fazla_mesai'] if hesaplama else 0}
                })
    except Exception as e:
        # swallow and render template with whatever we have
        pass

    form_adi = f"{year} Yılı {month}. Dönem {birim.BirimAdi} Çalışma Listesi"

    context = {
        'kurum': kurum,
        'dokuman_kodu': dokuman_kodu,
        'form_adi': form_adi,
        'yayin_tarihi': '01.01.2024',
        'revizyon_tarihi': '01.06.2024',
        'revizyon_no': '02',
        'sayfa_no': '1',
        'pdf_logo': pdf_logo,
        'personellers': personeller_for_pdf,
        'personeller': personeller_for_pdf,  # template expects 'personeller'
        'days': days,
        'resmi_tatil_gunleri': resmi_tatil_gunleri,
        'arefe_gunleri': arefe_gunleri,
        'year': year,
        'month': month,
        'liste': liste if 'liste' in locals() else None,
    }

    # Pdf oluştur
    template = get_template('mercis657/pdf/calisma_listesi.html')
    html = template.render({ **context })  # context sözlüğünü açarak gönder
    # PDF ayarları
    options = {
        'page-size': 'A4',
        'orientation': 'Landscape',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': True,
        'enable-external-links': True,
        'quiet': ''
    }

    # PDF oluştur
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    # HTTP response oluştur (open in new tab)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Cizelge_{year}_{month}.pdf"'
    return response

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

@login_required
def toplu_islem(request, liste_id, year, month):
    """Toplu işlemler modalını döner"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    liste = get_object_or_404(PersonelListesi, pk=liste_id)
    personeller = Personel.objects.filter(
        personellistesikayit__liste=liste
    ).distinct()
    mesai_tanimlari = Mesai_Tanimlari.objects.filter(GecerliMesai=True)

    # resmi tatil ve arefe günleri
    tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year, TatilTarihi__month=month
    )
    resmi_tatil_gunleri = [
        t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM'
    ]
    arefe_gunleri = [
        t.TatilTarihi.day for t in tatiller if t.ArefeMi
    ]

    context = {
        'liste': liste,
        'personeller': personeller,
        'mesai_tanimlari': mesai_tanimlari,
        'year': year,
        'month': month,
        'resmi_tatil_gunleri': resmi_tatil_gunleri,
        'extra_payload': {'liste_id': liste.id},  # her zaman dictionary
        'arefe_gunleri': arefe_gunleri,
        'disabled_days': [],  # toplu atamada genelde boş bırakabilirsin
        'toplu_mesai_ata_url': reverse(
            'mercis657:toplu_mesai_ata',
            args=[liste.id, year, month]
        ),
    }
    return render(request, 'mercis657/toplu_islem_modal.html', context)

@login_required
@require_POST
def toplu_radyasyon_ata(request, liste_id):
    """Tüm personele radyasyon çalışanı durumu atar"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        radyasyon_calisani = data.get('radyasyon_calisani', False)
        
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        updated_count = PersonelListesiKayit.objects.filter(
            liste=liste
        ).update(radyasyon_calisani=radyasyon_calisani)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{updated_count} personelin radyasyon durumu güncellendi.',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
@require_POST
def toplu_mesai_ata(request, liste_id, year, month):
    """Tüm personele toplu mesai atar (resmi tatiller hariç)"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

    try:
        data = json.loads(request.body)
        mesai_tanim_id = data.get('mesai_tanim_id')
        gunler = data.get('gunler', [])

        # Null veya geçersiz gün numaralarını ayıkla
        gunler = [int(g) for g in gunler if isinstance(g, int) and 1 <= g <= 31]

        if not mesai_tanim_id or not gunler:
            return JsonResponse({'status': 'error', 'message': 'Mesai tanımı ve günler seçilmelidir.'})

        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        mesai_tanim = get_object_or_404(Mesai_Tanimlari, pk=mesai_tanim_id)

        from datetime import date
        import calendar
        from hekim_cizelge.models import ResmiTatil  # kendi projendeki app yolunu kontrol et

        days_in_month = calendar.monthrange(year, month)[1]
        created_count = 0

        for personel in liste.kayitlar.all():
            for gun_no in gunler:
                # Ayın gün sınırını kontrol et
                if gun_no > days_in_month:
                    continue

                current_date = date(year, month, gun_no)

                # 📌 Resmi tatil kontrolü
                if ResmiTatil.objects.filter(TatilTarihi=current_date).exists():
                    continue  # resmi tatilde mesai yazma

                # Bu güne zaten mesai var mı kontrol et
                existing = Mesai.objects.filter(
                    Personel=personel.personel,
                    MesaiDate=current_date
                ).exists()

                if not existing:
                    Mesai.objects.create(
                        Personel=personel.personel,
                        MesaiDate=current_date,
                        MesaiTanim=mesai_tanim,
                        OnayDurumu=True,
                        Degisiklik=False
                    )
                    created_count += 1

        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} mesai kaydı oluşturuldu.',
            'created_count': created_count
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
