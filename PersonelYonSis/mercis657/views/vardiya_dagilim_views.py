from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template.loader import render_to_string
from ..models import Kurum, UstBirim, Idareci, Bina, Mesai, MesaiKontrol, PersonelListesiKayit
import json
from datetime import datetime
import pdfkit

@login_required
def vardiya_dagilim(request):
    """
    Vardiya dağılımı ana sayfası.
    Filtreleme seçeneklerini (select listeleri) context olarak gönderir.
    """
    context = {
        'kurumlar': Kurum.objects.filter(aktif=True),
        'ust_birimler': UstBirim.objects.filter(aktif=True),
        'idareciler': Idareci.objects.filter(aktif=True),
        'binalar': Bina.objects.filter(aktif=True),
        'bugun': datetime.now().strftime('%Y-%m-%d'),
    }
    return render(request, 'mercis657/vardiya_dagilim.html', context)

@login_required
@require_POST
def vardiya_dagilim_search(request):
    """
    AJAX endpoint: Filtrelere göre Mesai kayıtlarını sorgular.
    JSON input: {kurum_id, ust_birim_id, idareci_id, bina_id, tarih, vardiya}
    Response: {results: [{bina, birim, personeller: [...]}, ...]}
    """
    try:
        data = json.loads(request.body)
        kurum_id = data.get('kurum_id')
        ust_birim_id = data.get('ust_birim_id')
        idareci_id = data.get('idareci_id')
        bina_id = data.get('bina_id')
        tarih1 = data.get('tarih1')
        tarih2 = data.get('tarih2')
        vardiya_tipi = data.get('vardiya')  # 'gunduz', 'aksam', 'gece', 'tumu'
        mesai_notu = data.get('mesai_notu', [])

        if not tarih1 or not tarih2:
            return JsonResponse({'status': 'error', 'message': 'Tarih aralığı eksik'}, status=400)

        # Temel sorgu: Tarih aralığı ve geçerli mesai tanımı
        mesai_qs = Mesai.objects.filter(
            MesaiDate__range=[tarih1, tarih2],
            MesaiTanim__isnull=False,
            Izin__isnull=True  # İzinli olanlar hariç
        ).select_related(
            'Personel', 
            'MesaiTanim'
        ).prefetch_related('mesai_kontrolleri')

        # Vardiya tipi filtresi
        if vardiya_tipi == 'gunduz':
            mesai_qs = mesai_qs.filter(MesaiTanim__GunduzMesaisi=True)
        elif vardiya_tipi == 'aksam':
            mesai_qs = mesai_qs.filter(MesaiTanim__AksamMesaisi=True)
        elif vardiya_tipi == 'gece':
            mesai_qs = mesai_qs.filter(MesaiTanim__GeceMesaisi=True)

        if mesai_notu and len(mesai_notu) > 0:
            mesai_qs = mesai_qs.filter(MesaiNotu__in=mesai_notu)

        # PersonelListesiKayit üzerinden birim/bina filtreleme
        yil1, ay1 = int(tarih1.split('-')[0]), int(tarih1.split('-')[1])
        yil2, ay2 = int(tarih2.split('-')[0]), int(tarih2.split('-')[1])
        
        kayit_qs = PersonelListesiKayit.objects.filter(
            Q(liste__yil=yil1, liste__ay=ay1) | Q(liste__yil=yil2, liste__ay=ay2)
        ).select_related('liste__birim', 'liste__birim__Bina', 'personel')

        if kurum_id:
            kayit_qs = kayit_qs.filter(liste__birim__Kurum_id=kurum_id)
        if ust_birim_id:
            kayit_qs = kayit_qs.filter(liste__birim__UstBirim_id=ust_birim_id)
        if idareci_id:
            kayit_qs = kayit_qs.filter(liste__birim__Idareci_id=idareci_id)
        if bina_id:
            kayit_qs = kayit_qs.filter(liste__birim__Bina_id=bina_id)

        # Filtrelenen personellerin ID listesi
        personel_ids = kayit_qs.values_list('personel_id', flat=True)
        
        # Mesai sorgusunu bu personellerle sınırla
        mesai_qs = mesai_qs.filter(Personel_id__in=personel_ids)

        # Sonuçları grupla: Bina -> Birim -> Personel Listesi
        # Veriyi işlemek için dictionary kullanalım
        grouped_data = {}
        
        # PersonelListesiKayit verilerini memory'e alalım (personel_id -> birim bilgisi)
        personel_birim_map = {}
        for kayit in kayit_qs:
            birim = kayit.liste.birim
            bina_ad = birim.Bina.ad if birim.Bina else "Diğer"
            personel_birim_map[kayit.personel_id] = {
                'bina': bina_ad,
                'birim': birim.BirimAdi,
                'unvan': kayit.personel.PersonelTitle or ""
            }

        results = []
        
        for mesai in mesai_qs:
            p_info = personel_birim_map.get(mesai.Personel_id)
            if not p_info:
                continue # Listede olmayan ama mesaisi olan (eski kayıt vs) atla

            bina = p_info['bina']
            birim = p_info['birim']
            
            if bina not in grouped_data:
                grouped_data[bina] = {}
            if birim not in grouped_data[bina]:
                grouped_data[bina][birim] = []

            # Kontrol durumu
            kontrol_kaydi = mesai.mesai_kontrolleri.first()
            kontrol_durumu = kontrol_kaydi.kontrol if kontrol_kaydi else None

            grouped_data[bina][birim].append({
                'mesai_id': mesai.MesaiID,
                'personel_ad': f"{mesai.Personel.PersonelName} {mesai.Personel.PersonelSurname}",
                'unvan': p_info['unvan'],
                'mesai_tarih': mesai.MesaiDate.strftime('%d.%m.%Y'),
                'mesai_saat': mesai.MesaiTanim.Saat,
                'mesai_notu': mesai.MesaiNotu,
                'kontrol': kontrol_durumu
            })

        # Frontend formatına dönüştür
        sorted_binas = sorted(grouped_data.keys())
        final_results = []
        
        for bina in sorted_binas:
            birimler = grouped_data[bina]
            sorted_birims = sorted(birimler.keys())
            birim_list = []
            for birim_adi in sorted_birims:
                birim_list.append({
                    'ad': birim_adi,
                    'personeller': birimler[birim_adi]
                })
            final_results.append({
                'bina': bina,
                'birimler': birim_list
            })

        return JsonResponse({'status': 'success', 'results': final_results})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def vardiya_dagilim_kaydet(request):
    """
    AJAX endpoint: Gönderilen kontrol verilerini kaydeder.
    JSON input: [{mesai_id: 1, kontrol: true/false}, ...]
    """
    if not request.user.has_permission('ÇS 657 Vardiya Dağılımı Kontrolü'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok'}, status=403)
    try:
        data = json.loads(request.body)
        updates = data.get('updates', [])
        
        for item in updates:
            mesai_id = item.get('mesai_id')
            kontrol_val = item.get('kontrol')
            
            if mesai_id is not None and kontrol_val is not None:
                MesaiKontrol.objects.update_or_create(
                    mesai_id=mesai_id,
                    defaults={
                        'kontrol': kontrol_val,
                        'kontrol_yapan': request.user,
                        'kontrol_tarihi': datetime.now()
                    }
                )
                
        return JsonResponse({'status': 'success', 'message': 'Kayıtlar güncellendi.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def vardiya_dagilim_pdf(request):
    """
    Seçili filtrelerle PDF rapor oluşturur.
    GET params: kurum_id, ust_birim_id, idareci_id, bina_id, tarih, vardiya
    """
    try:
        kurum_id = request.GET.get('kurum_id')
        ust_birim_id = request.GET.get('ust_birim_id')
        idareci_id = request.GET.get('idareci_id')
        bina_id = request.GET.get('bina_id')
        tarih1 = request.GET.get('tarih1')
        tarih2 = request.GET.get('tarih2')
        vardiya_tipi = request.GET.get('vardiya')
        mesai_notu = request.GET.getlist('mesai_notu')
        
        if not tarih1 or not tarih2:
            bugun = datetime.now().strftime('%Y-%m-%d')
            tarih1 = bugun
            tarih2 = bugun

        # --- Filtreleme Mantığı (Search ile aynı) ---
        mesai_qs = Mesai.objects.filter(
            MesaiDate__range=[tarih1, tarih2],
            MesaiTanim__isnull=False,
            Izin__isnull=True
        ).select_related(
            'Personel', 
            'MesaiTanim'
        ).prefetch_related('mesai_kontrolleri')

        if vardiya_tipi == 'gunduz':
            mesai_qs = mesai_qs.filter(MesaiTanim__GunduzMesaisi=True)
        elif vardiya_tipi == 'aksam':
            mesai_qs = mesai_qs.filter(MesaiTanim__AksamMesaisi=True)
        elif vardiya_tipi == 'gece':
            mesai_qs = mesai_qs.filter(MesaiTanim__GeceMesaisi=True)

        if mesai_notu and len(mesai_notu) > 0:
            mesai_qs = mesai_qs.filter(MesaiNotu__in=mesai_notu)

        yil1, ay1 = int(tarih1.split('-')[0]), int(tarih1.split('-')[1])
        yil2, ay2 = int(tarih2.split('-')[0]), int(tarih2.split('-')[1])
        
        kayit_qs = PersonelListesiKayit.objects.filter(
            Q(liste__yil=yil1, liste__ay=ay1) | Q(liste__yil=yil2, liste__ay=ay2)
        ).select_related('liste__birim', 'liste__birim__Bina', 'personel')

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

        grouped_data = {}
        personel_birim_map = {}
        for kayit in kayit_qs:
            birim = kayit.liste.birim
            bina_ad = birim.Bina.ad if birim.Bina else "Diğer"
            personel_birim_map[kayit.personel_id] = {
                'bina': bina_ad,
                'birim': birim.BirimAdi,
                'unvan': kayit.personel.PersonelTitle or ""
            }

        for mesai in mesai_qs:
            p_info = personel_birim_map.get(mesai.Personel_id)
            if not p_info:
                continue 

            bina = p_info['bina']
            birim = p_info['birim']
            
            if bina not in grouped_data:
                grouped_data[bina] = {}
            if birim not in grouped_data[bina]:
                grouped_data[bina][birim] = []

            kontrol_kaydi = mesai.mesai_kontrolleri.first()
            kontrol_durumu = kontrol_kaydi.kontrol if kontrol_kaydi else None

            grouped_data[bina][birim].append({
                'mesai_id': mesai.MesaiID,
                'personel_ad': f"{mesai.Personel.PersonelName} {mesai.Personel.PersonelSurname}",
                'unvan': p_info['unvan'],
                'mesai_tarih': mesai.MesaiDate.strftime('%d.%m.%Y'),
                'mesai_saat': mesai.MesaiTanim.Saat,
                'kontrol': kontrol_durumu
            })

        sorted_binas = sorted(grouped_data.keys())
        final_results = []
        for bina in sorted_binas:
            birimler = grouped_data[bina]
            sorted_birims = sorted(birimler.keys())
            birim_list = []
            for birim_adi in sorted_birims:
                birim_list.append({
                    'ad': birim_adi,
                    'personeller': birimler[birim_adi]
                })
            final_results.append({
                'bina': bina,
                'birimler': birim_list
            })
        
        # --- PDF Oluşturma ---
        context = {
            'results': final_results,
            'tarih1': tarih1,
            'tarih2': tarih2,
            'vardiya': vardiya_tipi
        }
        html_string = render_to_string('mercis657/pdf/vardiya_dagilim_pdf.html', context)
        
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        options = {
            'page-size': 'A4',
            'encoding': "UTF-8",
            'footer-center': '[page] / [topage]',
            'footer-font-size': '10',
            'margin-bottom': '15mm',
            'margin-top': '15mm',
            'orientation': 'Portrait'
        }

        pdf = pdfkit.from_string(html_string, False, configuration=config, options=options)
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="vardiya_dagilim_{tarih1}_{tarih2}.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Hata oluştu: {str(e)}")
