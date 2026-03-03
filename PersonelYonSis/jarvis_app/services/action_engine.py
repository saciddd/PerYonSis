import json
from .llm_service import detect_intent_with_llm, summarize_data_with_llm

def process_action(message, request=None, history=[]):
    """
    Kullanıcıdan gelen mesajı analiz eder (intent detection),
    ilgili capability (yetenek) fonskyonunu çağırır ve
    çıkan sonucu bir dille harmanlayarak (LLM kullanarak) döner.
    """
    
    # 0. Yetki Kontrolü
    user = request.user if request else None
    if not user or not user.is_authenticated or not user.is_active:
        return {
            "type": "chat",
            "message": "Bu işlemi gerçekleştirmek için yetkiniz bulunmamaktadır."
        }

    # 1. Intent Detection
    intent_data = detect_intent_with_llm(message, history)
    
    # 2. Router / Dispatcher
    action_type = intent_data.get("type", "out_of_scope")
    intent = intent_data.get("intent")
    params = intent_data.get("parameters", {})
    
    if action_type == "action" and intent == "export_excel":
        return {
            "type": "action",
            "action_name": "download_excel",
            "message": "Tabii ki, istediğiniz raporu Excel formatında hazırlatıyorum. İndirme işlemi birazdan başlayacak."
        }
    
    if action_type == "chat":
        raw_result = "[SİSTEM NOTU]: Kullanıcı genel bir selamlama yaptı veya YönSis dışı bir şey söyledi. Kendini kısaca tanıt ve YönSis asistanı olduğunu belirt."
        final_response = summarize_data_with_llm(message, raw_result, history)
        return {"type": "chat", "message": final_response}
        
    if not intent_data or action_type == "out_of_scope":
        return {
            "type": "chat",
            "message": (
                "Merhaba, ben **YönSis** için tasarlanmış kurumsal yapay zeka asistanıyım. Algıladığım kadarıyla talebiniz tam olarak anlaşılamadı.\n\n"
                "💡 **Örnek Olarak Şunları Sorabilirsiniz:**\n"
                "• *Ahmet hangi birimde çalışıyor?*\n"
                "• *Sistemde şu an aktif kaç hekim (doktor) var?*\n"
                "• *Geçici görevli personelleri hangi birimlere vermişiz?*\n"
                "• *Engelli personellerin ünvanlarına göre dağılımı*"
            )
        }
    
    raw_result = "İşlem anlaşılamadı veya yetki yok."
    
    # 2. Router / Dispatcher
    try:
        if action_type == "query":
            raw_result = _route_query(intent, params, request)
        elif action_type == "command":
            raw_result = "Komut işleme şu anda devre dışı."
    except Exception as e:
        raw_result = f"Sistem hatası oluştu: {str(e)}"
    
    # 3. Sonucu LLM ile özetle / düzgün bir dilde sun
    final_response = summarize_data_with_llm(message, raw_result, history)
    
    if params.get("is_excel_export") is True:
        return {
            "type": "action",
            "action_name": "download_excel",
            "message": final_response
        }
    
    return {
        "type": "chat",
        "message": final_response
    }

def _route_query(intent, params, request):
    from .capabilities.dynamic_search import run_dynamic_search
    
    if intent in ["database_query", "dynamic_search"]:
        return run_dynamic_search(
            filters=params.get("filters"),
            is_active=params.get("is_active"),
            group_by=params.get("group_by"),
            explanation=params.get("explanation", "Bilinmeyen Neden"),
            request=request
        )
    
    return "Talep edilen veri sorgusu desteklenmiyor."
