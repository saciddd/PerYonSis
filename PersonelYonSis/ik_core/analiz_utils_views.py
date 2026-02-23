from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models.BirimYonetimi import PersonelBirim
from .models.personel import Personel, OzelDurum
import json

@login_required
@require_POST
def update_personel_birim_aciklama(request):
    try:
        data = json.loads(request.body)
        pb_id = data.get('personel_birim_id')
        aciklama = data.get('aciklama')
        
        if not pb_id:
             return JsonResponse({'status': 'error', 'message': 'ID eksik.'}, status=400)
             
        pb = get_object_or_404(PersonelBirim, id=pb_id)
        pb.not_text = aciklama
        pb.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def update_personel_ozel_durum(request):
    try:
        data = json.loads(request.body)
        personel_id = data.get('personel_id')
        ozel_durum_input = data.get('ozel_durumlar', []) # List of strings (IDs or Codes)
        
        if not personel_id:
            return JsonResponse({'status': 'error', 'message': 'Personel ID eksik.'}, status=400)
            
        personel = get_object_or_404(Personel, id=personel_id)
        
        from .models.valuelists import OZEL_DURUM_DEGERLERI
        mapping = dict(OZEL_DURUM_DEGERLERI)
        
        selected_objs = []
        for val in ozel_durum_input:
            val_str = str(val)
            
            # 1. Try to find by ID if val is numeric
            if val_str.isdigit():
                obj = OzelDurum.objects.filter(id=int(val_str)).first()
                if obj:
                    selected_objs.append(obj)
                    continue
            
            # 2. Try to find by kod in DB
            obj = OzelDurum.objects.filter(kod=val_str).first()
            if obj:
                selected_objs.append(obj)
                continue
                
            # 3. Try to find/create based on mapping from valuelists
            if val_str in mapping:
                ad = mapping[val_str]
                obj, created = OzelDurum.objects.get_or_create(kod=val_str, defaults={'ad': ad})
                selected_objs.append(obj)
        
        # Sync the relationship
        personel.ozel_durumu.set(selected_objs)
        personel.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
