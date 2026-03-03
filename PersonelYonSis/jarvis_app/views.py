import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .services.llm_service import generate_jarvis_response
from .services.action_engine import process_action

@login_required
def chat_view(request):
    """Render the main Jarvis chat application."""
    return render(request, 'jarvis_app/chat.html')

@csrf_exempt
@login_required
def api_chat(request):
    """Handle chat messages from frontend to Ollama backend."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            history = data.get("history", [])
            
            # Action Engine to check if user intent is a system action or just chat
            action = process_action(message, request, history)
            
            if action.get("type") == "chat":
                return JsonResponse({"status": "success", "response": action.get("message")})
            else:
                # E.g., handling navigation or other actions
                return JsonResponse({"status": "action", "action": action, "response": action.get("message", "İşlem gerçekleştirildi.")})
                
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@login_required
def export_excel_view(request):
    import openpyxl
    from django.http import HttpResponse
    
    # Session'daki son filtreyi alıyoruz
    last_search = request.session.get('jarvis_last_search')
    if not last_search:
        return HttpResponse("Oluşturulacak bir rapor bulunamadı. Lütfen önce Jarvis'e bir sorgu yapın.", status=400)
        
    filters = last_search.get("filters", {})
    is_active = last_search.get("is_active")
    
    from ik_core.models.personel import Personel
    queryset = Personel.objects.all()
    
    if filters:
        try:
            queryset = queryset.filter(**filters).distinct()
        except Exception as e:
            return HttpResponse(f"Rapor hazırlanırken geçerli olmayan bir kriter ({str(e)}) saptandı. Lütfen sorgunuzu yenileyin.", status=400)
            
    filtered_list = []
    for p in queryset.prefetch_related('unvan', 'brans'):
        durum = p.durum or ""
        if is_active is True:
            if "Aktif" in durum:
                filtered_list.append(p)
        elif is_active is False:
            if "Aktif" not in durum:
                filtered_list.append(p)
        else:
            filtered_list.append(p)
            
    # Excel Oluştur
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Jarvis Raporu"
    
    # Başlıklar
    headers = ["TC Kimlik No", "Ad", "Soyad", "Ünvan", "Branş", "Kadro Durumu", "Aktif/Pasif Durumu"]
    ws.append(headers)
    
    # Veriler
    for p in filtered_list:
        unvan_ad = p.unvan.ad if p.unvan else ""
        brans_ad = p.brans.ad if p.brans else ""
        kadro_drm = p.kadro_durumu or ""
        aktif_drm = p.durum or ""
        
        ws.append([
            p.tc_kimlik_no,
            p.ad,
            p.soyad,
            unvan_ad,
            brans_ad,
            kadro_drm,
            aktif_drm
        ])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="jarvis_personel_raporu.xlsx"'
    wb.save(response)
    return response
