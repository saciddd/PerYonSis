from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, F, Window
from django.db.models.functions import RowNumber
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .models.personel import Personel, KisaUnvan, UnvanBransEslestirme, Unvan, Brans
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

    # Base Queryset
    personeller = Personel.objects.all()

    # Apply Filters
    if durum_filter:
        # Implement logic for 'Durum' property filtering
        # Since 'durum' is a property, we might need to filter in Python or use specific logic
        # For efficiency, we can try to approximate or filter in python if dataset is small enough (< few thousands)
        # RFC says "Server-side pagination" implies large data, but property filtering is tough.
        # However, checking the property logic:
        # "Aktif" checks ayrilma_tarihi and gecicigorev.
        # We can implement Q objects for database filtering where possible.
        q_objs = Q()
        today = date.today()
        
        # This is a simplification. Fully replicating the property logic in ORM is complex.
        # We will try to filter the most reliable parts in ORM.
        if 'Kurumdan Ayrıldı' in durum_filter:
            q_objs |= Q(kadrolu_personel=True, ayrilma_tarihi__lte=today)
        
        # "Aktif" vs "Pasif" logic requires checking GeciciGorev which is complex relations.
        # For now, we will fetch and filter in python for complex properties if needed, 
        # or rely on basic attributes.
        # Let's try basic attributes first.
        pass

    # Note: Filtering by property 'durum' is expensive in DB. 
    # For now, let's filter what we can.
    
    if kisa_unvan_filter:
        personeller = personeller.filter(unvan_brans_eslestirme__kisa_unvan__id__in=kisa_unvan_filter)

    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
            personeller = personeller.filter(kadrolu_personel=False)

    # We need to filter by 'durum' property. 
    # Since we can't easily filter by property in ORM, we'll iterate.
    # But for aggregation, we need QuerySet.
    # Optimization: Helper function to get IDs of personels matching status
    if durum_filter:
        valid_ids = []
        for p in personeller:
             if p.durum in durum_filter:
                 valid_ids.append(p.id)
        personeller = personeller.filter(id__in=valid_ids)

    # Aggregations
    # 1. Kısa Ünvan Dağılımı
    kisa_unvan_dagilim = personeller.values(
        'unvan_brans_eslestirme__kisa_unvan__id', 
        'unvan_brans_eslestirme__kisa_unvan__ad'
    ).annotate(total=Count('id')).order_by('-total')

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
        'unvan_brans_eslestirme__kisa_unvan',
    ).prefetch_related('personelbirim_set', 'personelbirim_set__birim')

    for p in personeller_list:
        # Get Current Birim
        current_pb = p.personelbirim_set.order_by('-gecis_tarihi', '-creation_timestamp').first()
        if current_pb:
            birim_id = current_pb.birim.id
            birim_ad = current_pb.birim.ad
        else:
            birim_id = 'unknown'
            birim_ad = 'Tanımsız Birim'
            
        kisa_unvan = p.kisa_unvan # Property that returns string name
        # We need ID for better tracking, use relation
        if p.unvan_brans_eslestirme:
            ku_id = p.unvan_brans_eslestirme.kisa_unvan.id
            ku_ad = p.unvan_brans_eslestirme.kisa_unvan.ad
        else:
            ku_id = 'unknown'
            ku_ad = 'Tanımsız Ünvan'
            
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

    # Initial Kisa Unvan List for Modal
    active_kisa_unvans = KisaUnvan.objects.filter(
        id__in=personeller.values_list('unvan_brans_eslestirme__kisa_unvan_id', flat=True)
    ).distinct().order_by('ad')
    
    # All Kisa Unvans for filter dropdown (regardless of current filter)
    all_kisa_unvans_db = KisaUnvan.objects.all().order_by('ad')

    context = {
        'kisa_unvan_dagilim': kisa_unvan_dagilim,
        'matrix_rows': matrix_rows,
        'matrix_headers': sorted_kisa_unvans,
        'all_kisa_unvans': all_kisa_unvans_db, # For modal filter
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
    kisa_unvan_filter = request.GET.getlist('kisa_unvan', []) # Can be used as authority filter logic if mapped
    kadro_durumu_filter = request.GET.get('kadro_durumu', '')

    personeller = Personel.objects.all()
    
    # Apply Filters (Reuse logic or refactor to helper)
    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
             personeller = personeller.filter(kadrolu_personel=False)

    if kisa_unvan_filter:
        personeller = personeller.filter(unvan_brans_eslestirme__kisa_unvan__id__in=kisa_unvan_filter)

    if durum_filter:
        valid_ids = []
        for p in personeller:
             if p.durum in durum_filter:
                 valid_ids.append(p.id)
        personeller = personeller.filter(id__in=valid_ids)

    # Birim filtering needs to happen on the valid person set.
    # Since filter is "Birimin Bağlı Olduğu Üst Birim", we need to check current unit's parent.
    
    # Fetch data
    personeller_list = personeller.select_related(
        'unvan_brans_eslestirme__kisa_unvan',
    ).prefetch_related('personelbirim_set', 'personelbirim_set__birim', 'personelbirim_set__birim__ust_birim')
    
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
        
        # Data for Tab 2
        ku_id = p.unvan_brans_eslestirme.kisa_unvan.id if p.unvan_brans_eslestirme else 'unknown'
        
        if b_id not in birim_unvan_data:
            birim_unvan_data[b_id] = {'ad': b_ad, 'unvanlar': {}, 'total': 0}
            
        if ku_id not in birim_unvan_data[b_id]['unvanlar']:
            birim_unvan_data[b_id]['unvanlar'][ku_id] = 0
            
        birim_unvan_data[b_id]['unvanlar'][ku_id] += 1
        birim_unvan_data[b_id]['total'] += 1

    # Only include filtered people in context if needed, but we aggregated already.
    
    # View Filters
    ust_birimler = UstBirim.objects.all().order_by('ad')
    all_kisa_unvans = KisaUnvan.objects.all().order_by('ad')

    context = {
        'ust_birim_data': ust_birim_data,
        'birim_unvan_data': birim_unvan_data,
        'ust_birimler': ust_birimler,
        'all_kisa_unvans': all_kisa_unvans,
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
        'unvan', 'brans', 'unvan_brans_eslestirme', 'unvan_brans_eslestirme__kisa_unvan'
    ).prefetch_related('personelbirim_set', 'personelbirim_set__birim', 'ozel_durumu')

    # Apply Global Filters
    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
             personeller = personeller.filter(kadrolu_personel=False)

    if global_kisa_unvan:
        personeller = personeller.filter(unvan_brans_eslestirme__kisa_unvan__id__in=global_kisa_unvan)
        
    if durum_filter:
        valid_ids = []
        for p in personeller:
             if p.durum in durum_filter:
                 valid_ids.append(p.id)
        personeller = personeller.filter(id__in=valid_ids)
        
    # Apply Specific Filters (from cell click)
    if kisa_unvan_id and kisa_unvan_id != 'unknown':
        personeller = personeller.filter(unvan_brans_eslestirme__kisa_unvan__id=kisa_unvan_id)
        
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
