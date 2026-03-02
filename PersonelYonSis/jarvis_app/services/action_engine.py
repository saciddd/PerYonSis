import json
from .llm_service import detect_intent_with_llm, summarize_data_with_llm

def process_action(message, user=None):
    """
    Kullanıcıdan gelen mesajı analiz eder (intent detection),
    ilgili capability (yetenek) fonskyonunu çağırır ve
    çıkan sonucu bir dille harmanlayarak (LLM kullanarak) döner.
    """
    
    # 0. Yetki Kontrolü
    if not user or not user.is_authenticated or not user.is_active:
        return {
            "type": "chat",
            "message": "Bu işlemi gerçekleştirmek için yetkiniz bulunmamaktadır."
        }

    # 1. Intent Detection
    intent_data = detect_intent_with_llm(message)
    
    # 2. Router / Dispatcher
    action_type = intent_data.get("type", "out_of_scope")
    intent = intent_data.get("intent")
    params = intent_data.get("parameters", {})
    
    if not intent_data or action_type == "out_of_scope":
        return {
            "type": "chat",
            "message": (
                "Merhaba, ben **YönSis** için tasarlanmış kurumsal yapay zeka asistanıyım. Algıladığım kadarıyla talebiniz YönSis dışı bir konu veya tam olarak anlaşılamadı.\n\n"
                "💡 **Örnek Olarak Şunları Sorabilirsiniz:**\n"
                "• *Ahmet hangi birimde çalışıyor?*\n"
                "• *Sacit'in telefon numarası nedir?*\n"
                "• *Sistemde şu an aktif kaç hekim (doktor) var?*\n"
                "• *Acil serviste (veya bilgi işlemde) kaç kişi var?*\n"
                "• *Sacit hangi bölümde?*"
            )
        }
    
    raw_result = "İşlem anlaşılamadı veya yetki yok."
    
    # 2. Router / Dispatcher
    try:
        if action_type == "query":
            raw_result = _route_query(intent, params)
        elif action_type == "command":
            raw_result = "Komut işleme şu anda devre dışı."
    except Exception as e:
        raw_result = f"Sistem hatası oluştu: {str(e)}"
    
    # 3. Sonucu LLM ile özetle / düzgün bir dilde sun
    final_response = summarize_data_with_llm(message, raw_result)
    
    return {
        "type": "chat",
        "message": final_response
    }

def _route_query(intent, params):
    from .capabilities.personnel import get_person_department, get_person_phone
    from .capabilities.statistics import count_personnel_by_title, count_unit_personnel
    
    if intent == "get_person_department":
        return get_person_department(params.get("name"))
    
    elif intent == "get_person_phone":
        return get_person_phone(params.get("name"))
    
    elif intent == "count_by_title":
        # If the user says "doktor", we might want to map it to "tabip" for better ORM matching if needed, 
        # but the capability function can handle basic contains. Let's pass it directly.
        title_name = params.get("title_name")
        if title_name and title_name.lower() in ["doktor", "hekim"]:
            title_name = "tabip"
        return count_personnel_by_title(title_name)
    
    elif intent == "count_unit_personnel":
        return count_unit_personnel(params.get("unit_name"))
    
    return "Talep edilen veri sorgusu desteklenmiyor."
