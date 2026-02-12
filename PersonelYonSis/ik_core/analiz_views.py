from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q, F, Window
from django.db.models.functions import RowNumber
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from .models.personel import Personel, KisaUnvan, UnvanBransEslestirme
from .models.BirimYonetimi import Birim, UstBirim, PersonelBirim, Bina, Kampus
from datetime import date
import json
from django.template.loader import render_to_string

def serialize_personel_list(personels):
    """
    Frontend tarafında filtreleme ve listeleme yapmak için personelleri serialize eder.
    """
    data = []
    # Optimization: Prefetch already done in views usually, but for consistency:
    # We assume 'personels' is an iterable of Personel objects with necessary related fields populated.
    
    for p in personels:
        # Determine current unit logic (similar to views)
        # Using the cached property approach if available or calculating.
        # Since we are iterating, we can calculate 'son_birim' info.
        
        # We need a robust way to get current unit info for the JS filter.
        # In the views, we used logic like:
        # current_pb = p.personelbirim_set.order_by('-gecis_tarihi', '-creation_timestamp').first()
        # This is heavy to do one by one if not prefetched or annotated.
        # For the frontend list, we rely on the specific attributes we used in analysis.
        
        # However, to be safe and fast, let's use the object's loaded relationships.
        # We expect the queryset to have: .prefetch_related('personelbirim_set__birim__ust_birim', 'personelbirim_set__birim__bina')
        
        # Sort PBs in python to avoid DB hit per row
        pbs = sorted(
            [pb for pb in p.personelbirim_set.all()], 
            key=lambda x: (x.gecis_tarihi, x.creation_timestamp), 
            reverse=True
        )
        current_pb = pbs[0] if pbs else None
        
        birim_id = current_pb.birim.id if current_pb and current_pb.birim else 'unknown'
        birim_ad = current_pb.birim.ad if current_pb and current_pb.birim else 'Birim Atanmamış'
        ust_birim_id = current_pb.birim.ust_birim.id if current_pb and current_pb.birim and current_pb.birim.ust_birim else 'unknown'
        bina_id = current_pb.birim.bina.id if current_pb and current_pb.birim and current_pb.birim.bina else 'unknown'
        
        # Ozel durumlar
        ozel_durumlar = [{'ad': oz.ad} for oz in p.ozel_durumu.all()]
        
        # Unvan info
        # kisa_unvan property triggers DB if not careful, but usually we filter by it.
        # Let's trust kisa_unvan property or manual check.
        # p.kisa_unvan uses unvan-brans mapping.
        kisa_unvan_val = p.kisa_unvan or 'Tanımsız'
        # We need ID for filtering. The frontend will compare kisa_unvan_id.
        # We should map the text to ID? Or just use the calculated one if we have it in context.
        # The view usually passes filtered list.
        # Let's attach the kisa_unvan_id if we can, but p.kisa_unvan returns STRING.
        # We need a reverse lookup or include it in the object.
        # For simplicity, we can send kisa_unvan name and handle ID mapping in JS or send ID if we can deduce it.
        # Better: The view has `kisa_unvan_ad_to_id` map. We can use it if passed, but here we are in helper.
        # We will add checks for attributes set by the view.
        
        ku_id = getattr(p, '_kisa_unvan_id_cache', None) # We will set this in view loop
        if ku_id is None:
             # Fallback if view didn't annotate
             # This is slow, but safe.
             pass 

        data.append({
            'id': p.id,
            'ad_soyad': p.ad_soyad,
            'yas': p.yas or '-',
            'unvan_ad': p.unvan.ad if p.unvan else '-',
            'brans_ad': p.brans.ad if p.brans else '',
            'birim_id': str(birim_id), # str for JS comparison
            'birim_ad': birim_ad,
            'ust_birim_id': str(ust_birim_id),
            'bina_id': str(bina_id),
            'kisa_unvan_id': str(ku_id) if ku_id else 'unknown',
            'kisa_unvan_ad': str(kisa_unvan_val),
            'durum': p.durum,
            'aciklama': current_pb.not_text if current_pb and current_pb.not_text else '',
            'kadro_durumu': 'Kadrolu' if p.kadrolu_personel else 'Geçici Gelen',
            'ozel_durumlar': ozel_durumlar,
        })
    return data


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
    
    # Varsayılan Filtreler (AJAX dışı istekler için de filtre state'ini tutmamız lazım)
    # Check if this is an AJAX request for data
    load_data = request.GET.get('load_data') == '1'
    
    context = {
        'kisa_unvanlar': KisaUnvan.objects.select_related('ust_birim').order_by('ust_birim__ad', 'ad'),
        'ust_birimler': UstBirim.objects.all().order_by('ad'),
        'binalar': Bina.objects.all().order_by('ad'),
        'arama': {
            'kisa_unvan': [str(x) for x in kisa_unvan_filter],
        },
        'selected_kisa_unvans': [int(x) for x in kisa_unvan_filter],
        'selected_durum': durum_filter,
        'selected_kadro_durumu': kadro_durumu_filter,
    }

    if not load_data:
        # Initial Page Load - Return Skeleton
        return render(request, 'ik_core/analiz/unvan_analiz.html', context)

    # --- BELOW IS DATA CALCULATION (Only runs on AJAX) ---

    # Base Queryset
    personeller = Personel.objects.all()

    # Apply Filters - Önce DB filtreleri
    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
            personeller = personeller.filter(kadrolu_personel=False)
    
    if kisa_unvan_filter:
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
            personeller = personeller.filter(pk__in=[])

    # Durum filtresi ve Personel Listesi Hazırlığı
    # Genişletilmiş Prefetch
    personeller_list = list(personeller.select_related('unvan', 'brans').prefetch_related(
        'gecicigorev_set', 
        'personelbirim_set', 
        'personelbirim_set__birim', 
        'personelbirim_set__birim__ust_birim',
        'personelbirim_set__birim__bina',
        'ozel_durumu'
    ))
    
    valid_personels = []
    
    # Kisa unvan ve filter logic
    kisa_unvan_ad_to_id = {ku.ad: ku.id for ku in KisaUnvan.objects.all()}

    # Helper for fast lookups
    filtered_personel_objects = []

    for p in personeller_list:
        if durum_filter and p.durum not in durum_filter:
            continue
            
        # Attach Helpers for Serialization & Matrix
        ku_ad = p.kisa_unvan
        ku_id = kisa_unvan_ad_to_id.get(ku_ad, 'unknown')
        p._kisa_unvan_id_cache = ku_id
        
        filtered_personel_objects.append(p)

    # --- Aggregations ---

    # 1. Kısa Ünvan Dağılımı
    kisa_unvan_dagilim_dict = {}
    for p in filtered_personel_objects:
        ku_ad = p.kisa_unvan
        if ku_ad:
            if ku_ad not in kisa_unvan_dagilim_dict:
                kisa_unvan_dagilim_dict[ku_ad] = 0
            kisa_unvan_dagilim_dict[ku_ad] += 1
            
    kisa_unvan_dagilim = []
    for ku_ad, count in sorted(kisa_unvan_dagilim_dict.items(), key=lambda x: x[1], reverse=True):
        ku_id = kisa_unvan_ad_to_id.get(ku_ad, None)
        kisa_unvan_dagilim.append({
            'kisa_unvan_ad': ku_ad,
            'kisa_unvan_id': ku_id,
            'total': count
        })

    # 2. Birim - Kısa Ünvan Matrix
    matrix_data = {}
    all_kisa_unvans = set()

    for p in filtered_personel_objects:
        # Get Current Birim (optimized)
        pbs = sorted(
            [pb for pb in p.personelbirim_set.all()], 
            key=lambda x: (x.gecis_tarihi, x.creation_timestamp), 
            reverse=True
        )
        current_pb = pbs[0] if pbs else None

        if current_pb:
            birim_id = current_pb.birim.id
            birim_ad = current_pb.birim.ad
        else:
            birim_id = 'unknown'
            birim_ad = 'Tanımsız Birim'
            
        ku_id = p._kisa_unvan_id_cache
        ku_ad = p.kisa_unvan or 'Tanımsız Ünvan'
            
        if birim_id not in matrix_data:
            matrix_data[birim_id] = {'birim_ad': birim_ad, 'counts': {}, 'total': 0}
            
        if ku_id not in matrix_data[birim_id]['counts']:
             matrix_data[birim_id]['counts'][ku_id] = 0
             
        matrix_data[birim_id]['counts'][ku_id] += 1
        matrix_data[birim_id]['total'] += 1
        
        if ku_id != 'unknown':
            all_kisa_unvans.add((ku_id, ku_ad))

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

    # Prepare Context for partial Rendering
    # We render the Tables using render_to_string
    # We need to reuse the same context keys as the template expects
    
    partial_context = context.copy()
    partial_context.update({
        'kisa_unvan_dagilim': kisa_unvan_dagilim,
        'matrix_rows': matrix_rows,
        'matrix_headers': sorted_kisa_unvans,
    })
    
    # We need to extract the parts of the original template or create partials.
    # It is cleaner to return HTML strings for specific containers.
    # However, since the user wants a structural change, we can assume the existing template will be modified to accept this.
    # I will create simple partials or just return the data structure and let frontend render? 
    # NO, complex matrix is better rendered on server.
    
    # To avoid creating many new files, I'll render the whole 'unvan_analiz.html' but with a special block or 
    # simply render the content areas if I had them as partials.
    # The user didn't ask for partial files but I should probably create them for cleanliness.
    # But for now, to be minimally invasive, I will construct the HTML manually or use inline templates? No.
    # I will assume I can update the main template to wrap the dynamic parts in logic, OR
    # I will simply return the fully rendered tables as strings.
    
    # Since I don't have partials for the tables in `unvan_analiz.html` yet, I would have to extract them.
    # Better strategy: modify `unvan_analiz.html` to be mostly empty divs, and use JS to fill them.
    # I will create a new partial `partials/analiz_unvan_tables.html` effectively by splitting or just render the current logic if I can isolatedly.
    
    # Let's create a partial for the content of tabs.
    
    # IMPORTANT: The user wants "Data loading after page show".
    # I'll return:
    # 1. html_tab_dagilim
    # 2. html_tab_kirilim
    # 3. personel_data (JSON)
    
    # I'll use inline rendering or create a partial file in the next step.
    # For now in this VIEW update, I'll refer to a to-be-created partial: 'ik_core/partials/analiz_unvan_content.html'
    
    html_content = render_to_string('ik_core/partials/analiz_unvan_content.html', partial_context, request)
    personel_data = serialize_personel_list(filtered_personel_objects)
    
    return JsonResponse({
        'html_content': html_content,
        'personel_data': personel_data
    })


def birim_analiz_view(request):
    """
    Birim Bazlı Analiz Sayfası
    """
    # Initialize Filters
    durum_filter = request.GET.getlist('durum', [])
    ust_birim_filter = request.GET.getlist('ust_birim', [])
    kisa_unvan_filter = request.GET.getlist('kisa_unvan', [])
    kadro_durumu_filter = request.GET.get('kadro_durumu', '')
    
    # Varsayılan Filtreler
    # Check if this is an AJAX request for data
    load_data = request.GET.get('load_data') == '1'
    
    context = {
        'ust_birimler': UstBirim.objects.all().order_by('ad'),
        'kisa_unvanlar': KisaUnvan.objects.select_related('ust_birim').order_by('ust_birim__ad', 'ad'),
        'binalar': Bina.objects.all().order_by('ad'),
        'arama': {
            'kisa_unvan': [str(x) for x in kisa_unvan_filter],
        },
        'selected_durum': durum_filter,
        'selected_ust_birim': [int(x) for x in ust_birim_filter],
        'selected_kisa_unvans': [int(x) for x in kisa_unvan_filter],
        'selected_kadro_durumu': kadro_durumu_filter,
    }

    if not load_data:
        # Initial Page Load - Return Skeleton
        return render(request, 'ik_core/analiz/birim_analiz.html', context)
        
    # --- AJAX DATA CALCULATION ---

    personeller = Personel.objects.all()
    
    # Apply Filters
    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
            personeller = personeller.filter(kadrolu_personel=False)

    if kisa_unvan_filter:
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
            personeller = personeller.filter(pk__in=[])

    # Durum filtresi ve PREFETCH
    personeller_list = list(personeller.select_related('unvan', 'brans').prefetch_related(
        'gecicigorev_set', 
        'personelbirim_set', 
        'personelbirim_set__birim', 
        'personelbirim_set__birim__ust_birim',
        'personelbirim_set__birim__bina',
        'ozel_durumu'
    ))
    
    valid_personels = []
    
    # Kisa unvan ve filter logic
    kisa_unvan_ad_to_id = {ku.ad: ku.id for ku in KisaUnvan.objects.all()}
    
    selected_ust_birim_ids = [int(x) for x in ust_birim_filter]

    # Aggregations
    ust_birim_data = {}
    bina_data = {}
    all_kisa_unvans_set = set() # For compatibility
    
    filtered_personel_objects = []

    for p in personeller_list:
        if durum_filter and p.durum not in durum_filter:
            continue
            
        # Get Current Birim info for aggregation
        pbs = sorted(
            [pb for pb in p.personelbirim_set.all()], 
            key=lambda x: (x.gecis_tarihi, x.creation_timestamp), 
            reverse=True
        )
        current_pb = pbs[0] if pbs else None
        
        if not current_pb:
            continue
            
        birim = current_pb.birim
        ust_birim = birim.ust_birim
        
        if selected_ust_birim_ids and ust_birim.id not in selected_ust_birim_ids:
            continue
            
        # Attach helper for serialization
        ku_ad = p.kisa_unvan
        ku_id = kisa_unvan_ad_to_id.get(ku_ad, 'unknown')
        p._kisa_unvan_id_cache = ku_id
        
        filtered_personel_objects.append(p)
        
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
        bina_ad = birim.bina.ad if birim.bina else 'Tanımsız'
        birim_tipi = birim.birim_tipi or 'Tanımsız'
        
        if bina_ad not in bina_data:
            bina_data[bina_ad] = {}
            
        if birim_tipi not in bina_data[bina_ad]:
            bina_data[bina_ad][birim_tipi] = {'birimler': {}, 'total': 0}
            
        if b_id not in bina_data[bina_ad][birim_tipi]['birimler']:
            bina_data[bina_ad][birim_tipi]['birimler'][b_id] = {'ad': b_ad, 'unvanlar': {}, 'total': 0}
            
        if ku_id not in bina_data[bina_ad][birim_tipi]['birimler'][b_id]['unvanlar']:
            bina_data[bina_ad][birim_tipi]['birimler'][b_id]['unvanlar'][ku_id] = 0
            
        bina_data[bina_ad][birim_tipi]['birimler'][b_id]['unvanlar'][ku_id] += 1
        bina_data[bina_ad][birim_tipi]['birimler'][b_id]['total'] += 1
        bina_data[bina_ad][birim_tipi]['total'] += 1

    partial_context = context.copy()
    partial_context.update({
        'ust_birim_data': ust_birim_data,
        'bina_data': bina_data,
        'all_kisa_unvans': KisaUnvan.objects.all(), # Passed as QS in original but can be list
    })

    # Render Partial (Needs to be created, effectively content of tabs)
    html_content = render_to_string('ik_core/partials/analiz_birim_content.html', partial_context, request)
    personel_data = serialize_personel_list(filtered_personel_objects)
    
    return JsonResponse({
        'html_content': html_content,
        'personel_data': personel_data
    })


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
    bina_id = request.GET.get('bina_id')
    
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
        
    # Checking Birim / UstBirim / Bina involves fetching current unit
    if birim_id or ust_birim_id or bina_id:
        target_pids = []
        for p in personeller:
            current_pb = p.personelbirim_set.order_by('-gecis_tarihi', '-creation_timestamp').first()
            
            if birim_id == 'unknown':
                if not current_pb:
                    target_pids.append(p.id)
            elif birim_id:
                if current_pb and str(current_pb.birim.id) == str(birim_id):
                    target_pids.append(p.id)
            elif ust_birim_id:
                if current_pb and str(current_pb.birim.ust_birim.id) == str(ust_birim_id):
                    target_pids.append(p.id)
            elif bina_id:
                if current_pb and current_pb.birim.bina and str(current_pb.birim.bina.id) == str(bina_id):
                    target_pids.append(p.id)
        
        personeller = personeller.filter(id__in=target_pids)

    # Grouping by Last Unit (Birim)
    # We'll use a dictionary: { 'Birim Name': [personel_list], ... }
    
    grouped_personnel = {}
    
    # Sort personeller to make grouping easier or just iterate
    # Note: We can't rely on 'son_birim_kaydi' property for ORDER_BY in ORM easily because it is a property/computed.
    # So we iterate and group in Python.
    
    for p in personeller:
        # p.son_birim_kaydi uses the same logic: last PersonelBirim or "-"
        # Let's check for optimization. 'son_birim_kaydi' property uses DB hit if not optimized.
        # We did prefetch 'personelbirim_set' -> 'birim' in line 365, so it should be fast if property uses filtered set.
        # However, the property on model might do .last() which hits DB.
        # Let's stick effectively to what the template uses or what logic we have.
        
        # Optimized lookup from prefetched
        last_pb = None
        pbs = sorted(
            [pb for pb in p.personelbirim_set.all()], 
            key=lambda x: (x.gecis_tarihi, x.creation_timestamp), 
            reverse=True
        )
        if pbs:
            last_pb = pbs[0]
            # Attach for template
            p.aciklama = last_pb.not_text if last_pb.not_text else ''
            p.kisa_unvan_ad = p.kisa_unvan or 'Tanımsız'
            
        birim_name = "Birim Atanmamış"
        if last_pb:
            birim_name = f"{last_pb.birim.ad} ({last_pb.birim.bina.ad if last_pb.birim.bina else '?'})"
        
        if birim_name not in grouped_personnel:
            grouped_personnel[birim_name] = []
        grouped_personnel[birim_name].append(p)

    # Sort groups by name
    sorted_groups = dict(sorted(grouped_personnel.items()))

    context = {
        'grouped_personnel': sorted_groups,
        'total_count': len(personeller)
    }
    
    return render(request, 'ik_core/partials/analiz_personel_list_modal_content.html', context)

def kampus_analiz_view(request):
    """
    Kampüs / Görev Noktaları Analiz Sayfası
    """
    # Initialize Filters
    durum_filter = request.GET.getlist('durum', [])
    kampus_filter = request.GET.get('kampus', '') # Single selection for map view mostly
    kisa_unvan_filter = request.GET.getlist('kisa_unvan', [])
    kadro_durumu_filter = request.GET.get('kadro_durumu', '')
    
    # Varsayılan Filtreler
    # Check if this is an AJAX request for data
    load_data = request.GET.get('load_data') == '1'
    
     # Eğer Kampüs seçilmemişse, varsayılan olarak ilki veya hepsi? 
    if kampus_filter:
        aktif_kampus = get_object_or_404(Kampus, id=kampus_filter)
    else:
        aktif_kampus = Kampus.objects.first()

    context = {
        'kampusler': Kampus.objects.all(),
        'aktif_kampus': aktif_kampus,
        # Filters context
        'kisa_unvanlar': KisaUnvan.objects.select_related('ust_birim').order_by('ust_birim__ad', 'ad'),
        'selected_durum': durum_filter,
        'selected_kampus': int(aktif_kampus.id) if aktif_kampus else None,
        'selected_kisa_unvans': [int(x) for x in kisa_unvan_filter],
        'selected_kadro_durumu': kadro_durumu_filter,
    }
    
    if not load_data:
        return render(request, 'ik_core/analiz/kampus_analiz.html', context)

    # --- AJAX CALCULATION ---

    # 1. Personel Filtreleme
    personeller = Personel.objects.all()
    
    # Kadro Durumu
    if kadro_durumu_filter:
        if kadro_durumu_filter == 'Kadrolu':
            personeller = personeller.filter(kadrolu_personel=True)
        elif kadro_durumu_filter == 'Geçici Gelen':
            personeller = personeller.filter(kadrolu_personel=False)

    # Kısa Unvan
    if kisa_unvan_filter:
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
            personeller = personeller.filter(pk__in=[])

    # Durum and Prefetch
    personeller_list = list(personeller.select_related('unvan', 'brans').prefetch_related(
        'gecicigorev_set', 
        'personelbirim_set', 
        'personelbirim_set__birim', 
        'personelbirim_set__birim__bina',
        'personelbirim_set__birim__ust_birim',
        'ozel_durumu'
    ))
    
    filtered_personel_objects = []
    
    kisa_unvan_ad_to_id = {ku.ad: ku.id for ku in KisaUnvan.objects.all()}

     # 2. Bina Calculate
    bina_personel_counts = {} # { bina_id: count }
    bina_unit_counts = {} # { bina_id: { unit_name: count } }
    tanimsiz_personel_count = 0
    
    for p in personeller_list:
        if durum_filter and p.durum not in durum_filter:
            continue
            
        pbs = sorted(
            [pb for pb in p.personelbirim_set.all()], 
            key=lambda x: (x.gecis_tarihi, x.creation_timestamp), 
            reverse=True
        )
        current_pb = pbs[0] if pbs else None
        
        ku_ad = p.kisa_unvan
        ku_id = kisa_unvan_ad_to_id.get(ku_ad, 'unknown')
        p._kisa_unvan_id_cache = ku_id
        
        filtered_personel_objects.append(p)
        
        if current_pb and current_pb.birim and current_pb.birim.bina:
             b_id = current_pb.birim.bina.id
             bina_personel_counts[b_id] = bina_personel_counts.get(b_id, 0) + 1
             
             # Unit aggregations
             if b_id not in bina_unit_counts:
                 bina_unit_counts[b_id] = {}
             unit_name = current_pb.birim.ad
             bina_unit_counts[b_id][unit_name] = bina_unit_counts[b_id].get(unit_name, 0) + 1

        elif current_pb and current_pb.birim and not current_pb.birim.bina:
             # Birimi var ama binası yok -> Tanımsız bina
             tanimsiz_personel_count += 1
        else:
             # Birimi yok
             tanimsiz_personel_count += 1

    bina_verileri = []
    if aktif_kampus:
        binalar = aktif_kampus.binalar.all()
        for bina in binalar:
            count = bina_personel_counts.get(bina.id, 0)
            
            # Prepare unit list sorted by count
            units = bina_unit_counts.get(bina.id, {})
            sorted_units = sorted([{'ad': k, 'count': v} for k,v in units.items()], key=lambda x: x['count'], reverse=True)
            
            bina_verileri.append({
                'id': bina.id,
                'ad': bina.ad,
                'aciklama': bina.aciklama,
                'koordinatlar': bina.koordinatlar,
                'birim_sayisi': bina.birim_set.count(),
                'personel_sayisi': count,
                'kat_bilgisi': bina.aciklama,
                'birim_listesi_json': json.dumps(sorted_units)
            })

    partial_context = context.copy()
    partial_context.update({
        'bina_verileri': bina_verileri,
        'tanimsiz_personel_count': tanimsiz_personel_count
    })
    
    html_content = render_to_string('ik_core/partials/analiz_kampus_map.html', partial_context, request)
    personel_data = serialize_personel_list(filtered_personel_objects)
    
    return JsonResponse({
        'html_content': html_content,
        'personel_data': personel_data
    })

