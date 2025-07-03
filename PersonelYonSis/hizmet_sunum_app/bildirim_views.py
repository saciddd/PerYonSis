from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import HizmetSunumCalismasi  # Model adınızı kendi projenize göre güncelleyin

@require_POST
def bildirim_kesinlestir(request):
    """
    Tekil bildirim kaydı için kesinleştirme işlemi.
    POST: { "bildirim_id": ... }
    """
    import json
    try:
        data = json.loads(request.body)
        bildirim_id = data.get("bildirim_id")
        if not bildirim_id:
            return JsonResponse({"status": "error", "message": "Bildirim ID gerekli."}, status=400)
        bildirim = get_object_or_404(HizmetSunumCalismasi, CalismaId=bildirim_id)
        if getattr(bildirim, "Kesinlestirme", False):
            return JsonResponse({"status": "error", "message": "Kayıt zaten kesinleşmiş."}, status=400)
        bildirim.Kesinlestirme = True
        bildirim.save(update_fields=["Kesinlestirme"])
        return JsonResponse({"status": "success", "message": "Kayıt kesinleştirildi."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
def bildirim_kesinlestirmeyi_kaldir(request):
    """
    Tekil bildirim kaydı için kesinleştirmeyi kaldırma işlemi.
    POST: { "bildirim_id": ... }
    """
    import json
    try:
        data = json.loads(request.body)
        bildirim_id = data.get("bildirim_id")
        if not bildirim_id:
            return JsonResponse({"status": "error", "message": "Bildirim ID gerekli."}, status=400)
        bildirim = get_object_or_404(HizmetSunumCalismasi, CalismaId=bildirim_id)
        if not getattr(bildirim, "Kesinlestirme", False):
            return JsonResponse({"status": "error", "message": "Kayıt zaten beklemede."}, status=400)
        bildirim.Kesinlestirme = False
        bildirim.save(update_fields=["Kesinlestirme"])
        return JsonResponse({"status": "success", "message": "Kesinleştirme kaldırıldı."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)