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
            
            # Action Engine to check if user intent is a system action or just chat
            action = process_action(message, request.user)
            
            if action.get("type") == "chat":
                return JsonResponse({"status": "success", "response": action.get("message")})
            else:
                # E.g., handling navigation or other actions
                return JsonResponse({"status": "action", "action": action, "response": action.get("message", "İşlem gerçekleştirildi.")})
                
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
