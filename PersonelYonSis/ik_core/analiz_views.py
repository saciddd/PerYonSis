from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, F, Window
from django.db.models.functions import RowNumber
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .models.personel import Personel, KisaUnvan, UnvanBransEslestirme
from .models.BirimYonetimi import Birim, UstBirim, PersonelBirim
from datetime import date
import json

def dashboard_view(request):
    """
    Personel Analiz Dashboard Giriş Sayfası
    """
    return render(request, 'ik_core/analiz/dashboard.html')

def unvan_analiz_view(request):
    """
    Ünvan Bazlı Analiz Sayfası
    """
    # Initialize Filters
    durum_filter = request.GET.getlist('durum', [])
    kisa_unvan_filter = request.GET.getlist('kisa_unvan', [])
    kadro_durumu_filter = request.GET.get('kadro_durumu', '')
    
    # İlk açılışta varsayılan olarak sadece aktif personeller
    if not durum_filter and not kisa_unvan_filter and not kadro_durumu_filter:
        durum_filter = ['Aktif']

    # Base Queryset
    personeller = Personel.objects.all()

    # Apply Filters - Önce DB filtreleri (performans için)
    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
            personeller = personeller.filter(kadrolu_personel=False)
    
    if kisa_unvan_filter:
        # DB'de filtreleme yapmak için: Seçilen Kısa Unvan'lara ait Unvan-Branş eşleşmelerini bul
        eslesmeler = UnvanBransEslestirme.objects.filter(kisa_unvan_id__in=kisa_unvan_filter).values_list('unvan_id', 'brans_id')
        
        kisa_unvan_query = Q()
        for u_id, b_id in eslesmeler:
            if b_id:
                kisa_unvan_query |= Q(unvan_id=u_id, brans_id=b_id)
            else:
                kisa_unvan_query |= Q(unvan_id=u_id, brans__isnull=True)
        
        if kisa_unvan_query:
            personeller = personeller.filter(kisa_unvan_query)
        else:
            # Eşleşme yoksa boş döndür
            personeller = personeller.filter(pk__in=[])

    # Durum filtresi (property olduğu için Python tarafında)
    # Önce DB filtrelerini uygulayıp sonra durum filtresini uyguluyoruz (daha verimli)
    if durum_filter:
        # QuerySet'i listeye çevir ve durum property'sine göre filtrele
        # gecicigorev_set'i prefetch et çünkü durum property'si bunu kullanıyor
        personeller_list = list(personeller.select_related('unvan', 'brans').prefetch_related('gecicigorev_set'))
        valid_ids = []
        for p in personeller_list:
            if p.durum in durum_filter:
                valid_ids.append(p.id)
        personeller = Personel.objects.filter(id__in=valid_ids)

    # Aggregations
    # 1. Kısa Ünvan Dağılımı - kisa_unvan property'sine göre
    # Python tarafında hesaplama yapmalıyız çünkü property DB'de değil
    personeller_list_for_dagilim = personeller.select_related('unvan', 'brans')
    kisa_unvan_dagilim_dict = {}
    
    # Kısa unvan ID'lerini önceden bulalım (performans için)
    kisa_unvan_ad_to_id = {ku.ad: ku.id for ku in KisaUnvan.objects.all()}
    
    for p in personeller_list_for_dagilim:
        ku_ad = p.kisa_unvan
        if ku_ad:
            if ku_ad not in kisa_unvan_dagilim_dict:
                kisa_unvan_dagilim_dict[ku_ad] = 0
            kisa_unvan_dagilim_dict[ku_ad] += 1
    
    # Format for template: list of dicts (template uyumluluğu için)
    kisa_unvan_dagilim = []
    for ku_ad, count in sorted(kisa_unvan_dagilim_dict.items(), key=lambda x: x[1], reverse=True):
        ku_id = kisa_unvan_ad_to_id.get(ku_ad, None)
        kisa_unvan_dagilim.append({
            'kisa_unvan_ad': ku_ad,
            'kisa_unvan_id': ku_id,
            'total': count
        })

    # 2. Birim - Kısa Ünvan Kırılımı
    # We need current unit of each personel.
    # Since PersonelBirim is a history table, getting the CURRENT unit for aggregation is tricky.
    # We can pre-fetch current unit info.
    
    # Strategy: Get all PersonelBirim objects that are the 'latest' for each user 
    # within the filtered personel list.
    # Or, simpler: Iterate and build the matrix in Python.
    # Given the requirements for "Dynamic columns", this suggests Python construction anyway.
    
    matrix_data = {} # { BirimID: { 'birim_ad': ..., 'unvanlar': { KisaUnvanID: count } } }
    
    all_kisa_unvans = set()
    
    # Optimize: prefetch related
    personeller_list = personeller.select_related(
        'unvan', 'brans'
    ).prefetch_related('personelbirim_set', 'personelbirim_set__birim')

    # Kısa unvan ID'lerini önceden bulalım (performans için)
    kisa_unvan_ad_to_id = {ku.ad: ku.id for ku in KisaUnvan.objects.all()}

    for p in personeller_list:
        # Get Current Birim
        current_pb = p.personelbirim_set.order_by('-gecis_tarihi', '-creation_timestamp').first()
        if current_pb:
            birim_id = current_pb.birim.id
            birim_ad = current_pb.birim.ad
        else:
            birim_id = 'unknown'
            birim_ad = 'Tanımsız Birim'
            
        # kisa_unvan property'sini kullan
        ku_ad = p.kisa_unvan
        if ku_ad and ku_ad in kisa_unvan_ad_to_id:
            ku_id = kisa_unvan_ad_to_id[ku_ad]
        else:
            ku_id = 'unknown'
            ku_ad = ku_ad if ku_ad else 'Tanımsız Ünvan'
            
        if birim_id not in matrix_data:
            matrix_data[birim_id] = {'birim_ad': birim_ad, 'counts': {}, 'total': 0}
            
        if ku_id not in matrix_data[birim_id]['counts']:
             matrix_data[birim_id]['counts'][ku_id] = 0
             
        matrix_data[birim_id]['counts'][ku_id] += 1
        matrix_data[birim_id]['total'] += 1
        
        if ku_id != 'unknown':
            all_kisa_unvans.add((ku_id, ku_ad))

    # Format for template
    sorted_kisa_unvans = sorted(list(all_kisa_unvans), key=lambda x: x[1])
    
    matrix_rows = []
    for bid, data in matrix_data.items():
        row = {
            'birim_ad': data['birim_ad'],
            'birim_id': bid,
            'total': data['total'],
            'cols': []
        }
        for ku_id, ku_ad in sorted_kisa_unvans:
            count = data['counts'].get(ku_id, 0)
            row['cols'].append({
                'count': count,
                'ku_id': ku_id,
                'birim_id': bid
            })
        matrix_rows.append(row)
        
    matrix_rows.sort(key=lambda x: x['total'], reverse=True)

    # personel_list.html'deki gibi ust_birim'e göre sırala
    kisa_unvanlar = KisaUnvan.objects.select_related('ust_birim').order_by('ust_birim__ad', 'ad')

    context = {
        'kisa_unvan_dagilim': kisa_unvan_dagilim,
        'matrix_rows': matrix_rows,
        'matrix_headers': sorted_kisa_unvans,
        'kisa_unvanlar': kisa_unvanlar, # For modal filter - personel_list.html ile uyumlu
        'arama': {
            'kisa_unvan': [str(x) for x in kisa_unvan_filter], # Modal template'i için
        },
        'selected_kisa_unvans': [int(x) for x in kisa_unvan_filter],
        'selected_durum': durum_filter,
        'selected_kadro_durumu': kadro_durumu_filter,
    }

    return render(request, 'ik_core/analiz/unvan_analiz.html', context)

def birim_analiz_view(request):
    """
    Birim Bazlı Analiz Sayfası
    """
    # Initialize Filters
    durum_filter = request.GET.getlist('durum', [])
    ust_birim_filter = request.GET.getlist('ust_birim', [])
    kisa_unvan_filter = request.GET.getlist('kisa_unvan', [])
    kadro_durumu_filter = request.GET.get('kadro_durumu', '')
    
    # İlk açılışta varsayılan olarak sadece aktif personeller
    if not durum_filter and not ust_birim_filter and not kisa_unvan_filter and not kadro_durumu_filter:
        durum_filter = ['Aktif']

    personeller = Personel.objects.all()
    
    # Apply Filters - Önce DB filtreleri (performans için)
    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
            personeller = personeller.filter(kadrolu_personel=False)

    if kisa_unvan_filter:
        # DB'de filtreleme yapmak için: Seçilen Kısa Unvan'lara ait Unvan-Branş eşleşmelerini bul
        eslesmeler = UnvanBransEslestirme.objects.filter(kisa_unvan_id__in=kisa_unvan_filter).values_list('unvan_id', 'brans_id')
        
        kisa_unvan_query = Q()
        for u_id, b_id in eslesmeler:
            if b_id:
                kisa_unvan_query |= Q(unvan_id=u_id, brans_id=b_id)
            else:
                kisa_unvan_query |= Q(unvan_id=u_id, brans__isnull=True)
        
        if kisa_unvan_query:
            personeller = personeller.filter(kisa_unvan_query)
        else:
            # Eşleşme yoksa boş döndür
            personeller = personeller.filter(pk__in=[])

    # Durum filtresi (property olduğu için Python tarafında)
    # Önce DB filtrelerini uygulayıp sonra durum filtresini uyguluyoruz (daha verimli)
    if durum_filter:
        # QuerySet'i listeye çevir ve durum property'sine göre filtrele
        # gecicigorev_set'i prefetch et çünkü durum property'si bunu kullanıyor
        personeller_list = list(personeller.select_related('unvan', 'brans').prefetch_related('gecicigorev_set'))
        valid_ids = []
        for p in personeller_list:
            if p.durum in durum_filter:
                valid_ids.append(p.id)
        personeller = Personel.objects.filter(id__in=valid_ids)

    # Birim filtering needs to happen on the valid person set.
    # Since filter is "Birimin Bağlı Olduğu Üst Birim", we need to check current unit's parent.
    
    # Fetch data
    personeller_list = personeller.select_related(
        'unvan', 'brans'
    ).prefetch_related('personelbirim_set', 'personelbirim_set__birim', 'personelbirim_set__birim__ust_birim')
    
    # Kısa unvan ID'lerini önceden bulalım (performans için)
    kisa_unvan_ad_to_id = {ku.ad: ku.id for ku in KisaUnvan.objects.all()}
    
    # Aggregations
    # Tab 1: Üst Birim -> Birim Dağılımı
    ust_birim_data = {}
    
    # Tab 2: Birim -> Ünvan Dağılımı (Similar to Matrix in Unvan Analiz)
    birim_unvan_data = {}
    
    # Filter by Ust Birim here in Python loop if complex, or ID list
    selected_ust_birim_ids = [int(x) for x in ust_birim_filter]

    filtered_personel_ids = []

    for p in personeller_list:
        current_pb = p.personelbirim_set.order_by('-gecis_tarihi', '-creation_timestamp').first()
        
        if not current_pb:
            continue
            
        birim = current_pb.birim
        ust_birim = birim.ust_birim
        
        if selected_ust_birim_ids and ust_birim.id not in selected_ust_birim_ids:
            continue
            
        filtered_personel_ids.append(p.id)
        
        # Data for Tab 1
        ub_id = ust_birim.id
        ub_ad = ust_birim.ad
        b_id = birim.id
        b_ad = birim.ad
        
        if ub_id not in ust_birim_data:
            ust_birim_data[ub_id] = {'ad': ub_ad, 'birimler': {}, 'total': 0}
            
        if b_id not in ust_birim_data[ub_id]['birimler']:
            ust_birim_data[ub_id]['birimler'][b_id] = {'ad': b_ad, 'count': 0}
            
        ust_birim_data[ub_id]['birimler'][b_id]['count'] += 1
        ust_birim_data[ub_id]['total'] += 1
        
        # Data for Tab 2 - kisa_unvan property'sini kullan
        ku_ad = p.kisa_unvan
        if ku_ad and ku_ad in kisa_unvan_ad_to_id:
            ku_id = kisa_unvan_ad_to_id[ku_ad]
        else:
            ku_id = 'unknown'
        
        if b_id not in birim_unvan_data:
            birim_unvan_data[b_id] = {'ad': b_ad, 'unvanlar': {}, 'total': 0}
            
        if ku_id not in birim_unvan_data[b_id]['unvanlar']:
            birim_unvan_data[b_id]['unvanlar'][ku_id] = 0
            
        birim_unvan_data[b_id]['unvanlar'][ku_id] += 1
        birim_unvan_data[b_id]['total'] += 1

    # Only include filtered people in context if needed, but we aggregated already.
    
    # View Filters
    ust_birimler = UstBirim.objects.all().order_by('ad')
    # personel_list.html'deki gibi ust_birim'e göre sırala
    kisa_unvanlar = KisaUnvan.objects.select_related('ust_birim').order_by('ust_birim__ad', 'ad')

    context = {
        'ust_birim_data': ust_birim_data,
        'birim_unvan_data': birim_unvan_data,
        'ust_birimler': ust_birimler,
        'kisa_unvanlar': kisa_unvanlar, # For modal filter - personel_list.html ile uyumlu
        'all_kisa_unvans': kisa_unvanlar, # Tab 2 için backward compatibility
        'arama': {
            'kisa_unvan': [str(x) for x in kisa_unvan_filter], # Modal template'i için
        },
        'selected_durum': durum_filter,
        'selected_ust_birim': selected_ust_birim_ids,
        'selected_kisa_unvans': [int(x) for x in kisa_unvan_filter],
        'selected_kadro_durumu': kadro_durumu_filter,
    }
    
    return render(request, 'ik_core/analiz/birim_analiz.html', context)

def personel_list_modal_view(request):
    """
    Tablo hücrelerine tıklandığında açılan modal içeriğini döndürür.
    Args:
    - birim_id (optional)
    - kisa_unvan_id (optional)
    - ust_birim_id (optional)
    - global filter params...
    """
    
    birim_id = request.GET.get('birim_id')
    kisa_unvan_id = request.GET.get('kisa_unvan_id')
    ust_birim_id = request.GET.get('ust_birim_id')
    
    # Global Filters
    durum_filter = request.GET.getlist('durum', [])
    kadro_durumu_filter = request.GET.get('kadro_durumu', '')
    global_kisa_unvan = request.GET.getlist('kisa_unvan', []) # From global filter

    personeller = Personel.objects.all().select_related(
        'unvan', 'brans'
    ).prefetch_related('personelbirim_set', 'personelbirim_set__birim', 'ozel_durumu')

    # Apply Global Filters
    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
             personeller = personeller.filter(kadrolu_personel=False)

    if global_kisa_unvan:
        # DB'de filtreleme yapmak için: Seçilen Kısa Unvan'lara ait Unvan-Branş eşleşmelerini bul
        eslesmeler = UnvanBransEslestirme.objects.filter(kisa_unvan_id__in=global_kisa_unvan).values_list('unvan_id', 'brans_id')
        
        kisa_unvan_query = Q()
        for u_id, b_id in eslesmeler:
            if b_id:
                kisa_unvan_query |= Q(unvan_id=u_id, brans_id=b_id)
            else:
                kisa_unvan_query |= Q(unvan_id=u_id, brans__isnull=True)
        
        if kisa_unvan_query:
            personeller = personeller.filter(kisa_unvan_query)
        else:
            # Eşleşme yoksa boş döndür
            personeller = personeller.filter(pk__in=[])
        
    if durum_filter:
        valid_ids = []
        for p in personeller:
             if p.durum in durum_filter:
                 valid_ids.append(p.id)
        personeller = personeller.filter(id__in=valid_ids)
        
    # Apply Specific Filters (from cell click)
    if kisa_unvan_id and kisa_unvan_id != 'unknown':
        # DB'de filtreleme yapmak için: Seçilen Kısa Unvan'a ait Unvan-Branş eşleşmelerini bul
        eslesmeler = UnvanBransEslestirme.objects.filter(kisa_unvan_id=kisa_unvan_id).values_list('unvan_id', 'brans_id')
        
        kisa_unvan_query = Q()
        for u_id, b_id in eslesmeler:
            if b_id:
                kisa_unvan_query |= Q(unvan_id=u_id, brans_id=b_id)
            else:
                kisa_unvan_query |= Q(unvan_id=u_id, brans__isnull=True)
        
        if kisa_unvan_query:
            personeller = personeller.filter(kisa_unvan_query)
        else:
            # Eşleşme yoksa boş döndür
            personeller = personeller.filter(pk__in=[])
        
    # Checking Birim / UstBirim involves fetching current unit
    if birim_id or ust_birim_id:
        target_pids = []
        for p in personeller:
            current_pb = p.personelbirim_set.order_by('-gecis_tarihi', '-creation_timestamp').first()
            if not current_pb:
                continue
            
            if birim_id:
                if str(current_pb.birim.id) == str(birim_id):
                    target_pids.append(p.id)
            elif ust_birim_id:
                if str(current_pb.birim.ust_birim.id) == str(ust_birim_id):
                    target_pids.append(p.id)
        
        personeller = personeller.filter(id__in=target_pids)

    context = {
        'personeller': personeller
    }
    
    return render(request, 'ik_core/partials/analiz_personel_list_modal_content.html', context)
