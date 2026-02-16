from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models.BirimYonetimi import PersonelBirim
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
