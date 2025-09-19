from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from PersonelYonSis.views import get_user_permissions
from ..models import Bildirim, Kurum, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin, UstBirim
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Prefetch
from decimal import Decimal
from mercis657.utils import hesapla_fazla_mesai
import os
import openpyxl
from io import BytesIO
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

def raporlama(request):
    bildirimler_by_birim = None
    donem = None
    kurum = None
    idare = None
    excel_url = None
    error_message = None
    info_message = None
    birimler_json = None
    birimler = Birim.objects.all()
    kurumlar = Kurum.objects.all()
    idareler = UstBirim.objects.all()

    # Form yerine GET parametrelerini doğrudan al
    donem_str = request.GET.get('donem')
    kurum = request.GET.get('kurum')
    idare = request.GET.get('idare')
    durum = request.GET.get('durum')  # "1", "0" veya ""

    toplam_kayit = 0

    # Dönem parametresi varsa veriyi çek
    if donem_str:
        try:
            # 'YYYY-MM' formatındaki stringi ayın ilk günü olan date objesine çevir
            donem = datetime.strptime(donem_str, "%Y-%m").date()

            bildirimler_query = Bildirim.objects.select_related(
                'Personel',
                'PersonelListesi__birim',
            ).filter(
                 DonemBaslangic=donem
            )

            if kurum:
                bildirimler_query = bildirimler_query.filter(
                    PersonelListesi__birim__KurumAdi=kurum
                )
            if idare:
                bildirimler_query = bildirimler_query.filter(
                    PersonelListesi__birim__IdareAdi=idare
                )

            if durum == "1":
                bildirimler_query = bildirimler_query.filter(OnayDurumu=1)
            elif durum == "0":
                bildirimler_query = bildirimler_query.filter(OnayDurumu=0)

            # Bildirimleri çek ve PersonelListesi__birim'e göre grupla (Birim modelinde doğrudan bildirim_set yok)
            birim_ids_with_calisma = list(bildirimler_query.values_list('PersonelListesi__birim', flat=True).distinct())

            birimler_with_bildirimler = Birim.objects.filter(BirimID__in=birim_ids_with_calisma).order_by('BirimAdi')

            # Bildirimleri sıralı çek ve Python tarafında birim id'lerine göre grupla
            bildirimler_list = list(bildirimler_query.order_by('Personel__PersonelName').select_related('Personel', 'PersonelListesi'))
            bildirimler_map = {}
            for b in bildirimler_list:
                try:
                    birim_obj = getattr(b.PersonelListesi, 'birim', None)
                    birim_id = birim_obj.BirimID if birim_obj is not None else None
                except Exception:
                    birim_id = None
                if birim_id is None:
                    continue
                bildirimler_map.setdefault(birim_id, []).append(b)

            # Birimleri JSON'a çevir
            birimler_json = json.dumps([
                {'BirimID': b.BirimID, 'BirimAdi': b.BirimAdi} for b in birimler_with_bildirimler
            ])

            bildirimler_by_birim = []
            for birim in birimler_with_bildirimler:
                items = bildirimler_map.get(birim.BirimID, [])
                if items:
                    onaylanmis = sum(1 for c in items if c.OnayDurumu == 1)
                    beklemede = sum(1 for c in items if c.OnayDurumu == 0)
                    bildirimler_by_birim.append({
                        'birim': birim,
                        'bildirimler': items,
                        'personel_sayisi': len(set([getattr(c.Personel, 'PersonelID', None) for c in items])),
                        'onaylanmis_sayisi': onaylanmis,
                        'beklemede_sayisi': beklemede,
                    })

            toplam_kayit = sum(len(birim['bildirimler']) for birim in bildirimler_by_birim)

            # Excel indirme linki oluştur
            if bildirimler_by_birim:
                 excel_url = reverse('hizmet_sunum_app:export_raporlama_excel')
                 excel_url += f'?donem={donem.strftime("%Y-%m")}'

                 if kurum:
                     excel_url += f'&kurum={kurum}'
                 if durum:
                     excel_url += f'&durum={durum}'
                 if idare:
                     excel_url += f'&idare={idare}'

            if toplam_kayit == 0:
                 info_message = "Seçilen dönem ve kuruma ait hizmet sunum çalışması bulunamadı."

        except ValueError:
             error_message = "Geçersiz dönem formatı seçildi."
        except Exception as e:
            # Hata yönetimi
            error_message = f"Rapor oluşturulurken bir hata oluştu: {str(e)}"
            print(f"Raporlama Hatası: {e}") # Konsola yazdır (geliştirme için)
    else:
        # İlk sayfa yüklemesi veya dönem seçilmemişse
        info_message = "Lütfen bir dönem ve isteğe bağlı kriterlerinizi seçerek raporlayın."

    kesinlestirme_yetkisi = request.user.has_permission('HSA Bildirim Kesinleştirme')
    context = {
        # 'form': form, # Form kaldırıldı
        'bildirimler_by_birim': bildirimler_by_birim,
        'birimler': birimler, # Kurum seçimi için tüm birimleri geçiyoruz (kurum listesi çekmek için)
        'birimler_json': birimler_json,
        'kurumlar': kurumlar, # Kurum seçimi için tüm kurumları geçiyoruz
        'idareler': idareler,
        'selected_donem': donem_str, # Şablona dönemin string halini gönderelim ki selectbox'ta seçili kalsın
        'selected_kurum': kurum,
        'selected_idare': idare,
        'selected_durum': durum,
        'excel_url': excel_url,
        # 'is_form_valid': is_form_valid, # Form kaldırıldı
        'error_message': error_message,
        'info_message': info_message,
        'toplam_kayit': toplam_kayit,
        'kesinlestirme_yetkisi': kesinlestirme_yetkisi,
    }
    return render(request, 'mercis657/raporlama.html', context)

def export_raporlama_excel(request):
    # New implementation using mercis657.Bildirim model and openpyxl
    donem_str = request.GET.get('donem')
    kurum = request.GET.get('kurum')
    idare = request.GET.get('idare')

    if not donem_str:
        messages.error(request, "Lütfen bir dönem seçin.")
        return redirect('mercis657:raporlama')

    try:
        donem = datetime.strptime(donem_str, "%Y-%m").date()
    except ValueError:
        messages.error(request, "Geçersiz dönem formatı.")
        return redirect('mercis657:raporlama')

    # Fetch Bildirim queryset for the period
    bildirimler_qs = Bildirim.objects.select_related('Personel', 'PersonelListesi__birim').filter(DonemBaslangic=donem)
    if kurum:
        bildirimler_qs = bildirimler_qs.filter(PersonelListesi__birim__Kurum__ad=kurum)
    if idare:
        bildirimler_qs = bildirimler_qs.filter(PersonelListesi__birim__UstBirim__ad=idare)

    if not bildirimler_qs.exists():
        messages.warning(request, "Seçilen filtreye uygun veri bulunamadı.")
        return redirect('mercis657:raporlama')

    # Openpyxl workbook creation using a basic template or new workbook
    template_path = os.path.join(settings.BASE_DIR, 'static', 'excels', 'FazlaMesaiSablon.xlsx')
    if os.path.exists(template_path):
        wb = openpyxl.load_workbook(template_path)
        ws = wb.active
    else:
        # Create a minimal workbook if template not found
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'FazlaMesai'

    # Write header row according to FazlaMesaiSablon expectations
    headers = ["PersonelTCKN", "PersonelAd", "PersonelUnvan", "Kurum", "UstBirim", "BirimAdi",
               "NormalFazlaMesai","BayramFazlaMesai","RiskliNormalFazlaMesai","RiskliBayramFazlaMesai",
               "NormalIcap","BayramIcap"]
    for col, h in enumerate(headers, start=1):
        ws.cell(row=1, column=col, value=h)

    row = 2
    # Group by bildirim kod if such field exists; assumption: Bildirim has no explicit 'kod' field, so group by PersonelListesi
    for b in bildirimler_qs.order_by('PersonelListesi__birim__BirimAdi', 'Personel__PersonelName'):
        # Skip null/zero values as requested
        values = {
            'PersonelTCKN': getattr(b.Personel, 'PersonelTCKN', None),
            'PersonelAd': getattr(b.Personel, 'PersonelName', None),
            'PersonelUnvan': getattr(b.Personel, 'PersonelTitle', None),
            'Kurum': getattr(getattr(b.PersonelListesi, 'birim', None), 'Kurum', None),
            'UstBirim': getattr(getattr(b.PersonelListesi, 'birim', None), 'UstBirim', None),
            'BirimAdi': getattr(getattr(b.PersonelListesi, 'birim', None), 'BirimAdi', None),
            'NormalFazlaMesai': float(b.NormalFazlaMesai) if b.NormalFazlaMesai else None,
            'BayramFazlaMesai': float(b.BayramFazlaMesai) if b.BayramFazlaMesai else None,
            'RiskliNormalFazlaMesai': float(b.RiskliNormalFazlaMesai) if b.RiskliNormalFazlaMesai else None,
            'RiskliBayramFazlaMesai': float(b.RiskliBayramFazlaMesai) if b.RiskliBayramFazlaMesai else None,
            'NormalIcap': float(b.NormalIcap) if b.NormalIcap else None,
            'BayramIcap': float(b.BayramIcap) if b.BayramIcap else None,
        }

        # Determine row color for KadroDurumu == 'Geçici Gelen'
        kadro = None
        try:
            # Assumption: Personel model may have 'KadroDurumu' attribute; otherwise skip coloring
            kadro = getattr(b.Personel, 'KadroDurumu', None)
        except Exception:
            kadro = None

        # Write only non-null values; map to columns
        col = 1
        for key in ['PersonelTCKN','PersonelAd','PersonelUnvan','Kurum','UstBirim','BirimAdi',
                    'NormalFazlaMesai','BayramFazlaMesai','RiskliNormalFazlaMesai','RiskliBayramFazlaMesai',
                    'NormalIcap','BayramIcap']:
            val = values.get(key)
            if val is None or (isinstance(val, (int, float)) and val == 0):
                # leave cell blank
                ws.cell(row=row, column=col, value=None)
            else:
                ws.cell(row=row, column=col, value=val)
            col += 1

        # Apply green fill if KadroDurumu == 'Geçici Gelen'
        if kadro == 'Geçici Gelen':
            from openpyxl.styles import PatternFill
            fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
            for c in range(1, col):
                ws.cell(row=row, column=c).fill = fill

        row += 1

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name = f"FazlaMesaiSablon_{donem_str}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response


@require_POST
@login_required
def update_birim_kodlari(request):
    """Endpoint: Güncellenen birim kodlarını alır ve kaydeder.
    Beklenen payload: {'birim_id': id, 'NormalNobetKodu': val, 'BayramNobetKodu': val,...}
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        birim_id = data.get('birim_id')
        birim = Birim.objects.get(BirimID=birim_id)

        # Permission check: kullanıcı birim bilgilerini düzenleyebilmeli
        if not request.user.has_perm('mercis657.birim_bilgilerini_duzenleyebilir'):
            return JsonResponse({'status':'error','message':'Yetkiniz yok'}, status=403)

        # Update allowed fields
        for field in ['NormalNobetKodu','BayramNobetKodu','RiskliNormalNobetKodu','RiskliBayramNobetKodu']:
            if field in data:
                val = data[field]
                setattr(birim, field, val)
        birim.save()
        return JsonResponse({'status':'success','message':'Birim bilgileri güncellendi'})
    except Birim.DoesNotExist:
        return JsonResponse({'status':'error','message':'Birim bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({'status':'error','message':str(e)}, status=500)


@require_POST
@login_required
def kilit_tekil(request):
    """Endpoint: Verilen birim için seçilen dönemdeki Bildirimlerin MutemetKilit alanını toggle eder.
    Payload: {'birim_id': id, 'donem': 'YYYY-MM', 'action': optional 'lock'|'unlock'}
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        birim_id = data.get('birim_id')
        donem_str = data.get('donem')
        action = data.get('action')
        donem = datetime.strptime(donem_str, "%Y-%m").date()

        bildirimler = Bildirim.objects.filter(PersonelListesi__birim__BirimID=birim_id, DonemBaslangic=donem)
        if not bildirimler.exists():
            return JsonResponse({'status':'error','message':'Bildirim bulunamadı'}, status=404)

        with transaction.atomic():
            for b in bildirimler:
                if action == 'unlock':
                    b.MutemetKilit = False
                    b.MutemetKilitUser = None
                    b.MutemetKilitTime = None
                else:
                    b.MutemetKilit = True
                    b.MutemetKilitUser = request.user
                    b.MutemetKilitTime = timezone.now()
                b.save()

        return JsonResponse({'status':'success','message':'Kilit durumu güncellendi'})
    except Exception as e:
        return JsonResponse({'status':'error','message':str(e)}, status=500)


@require_POST
@login_required
def kilit_toplu(request):
    """Endpoint: Tüm bildirimleri döneme göre kilitle veya aç.
    Payload: {'donem': 'YYYY-MM', 'action': 'lock'|'unlock'}
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        donem_str = data.get('donem')
        action = data.get('action')
        donem = datetime.strptime(donem_str, "%Y-%m").date()

        bildirimler = Bildirim.objects.filter(DonemBaslangic=donem)
        if not bildirimler.exists():
            return JsonResponse({'status':'error','message':'Bildirim bulunamadı'}, status=404)

        with transaction.atomic():
            for b in bildirimler:
                if action == 'unlock':
                    b.MutemetKilit = False
                    b.MutemetKilitUser = None
                    b.MutemetKilitTime = None
                else:
                    b.MutemetKilit = True
                    b.MutemetKilitUser = request.user
                    b.MutemetKilitTime = timezone.now()
                b.save()

        return JsonResponse({'status':'success','message':'Toplu işlem tamamlandı'})
    except Exception as e:
        return JsonResponse({'status':'error','message':str(e)}, status=500)
