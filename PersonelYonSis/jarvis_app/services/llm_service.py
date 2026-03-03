import requests
import json
import re

# --- AI MODÜL SEÇİMİ ---
# "local"  = Yerel Ollama (gemma3:4b) kullanır. Ücretsizdir, internet gerektirmez ancak yavaş/donanım bağımlısıdır.
# "online" = Google Gemini API (gemini-2.5-flash) kullanır. Çok hızlıdır ve mantıksal kapasitesi yüksektir.
LLM_MODE = "local"

# --- GEMINI (Online) AYARLARI ---
GEMINI_API_KEY = "AIzaSyC7Nhpa55UmoLBGtXWGE1ItB_t8atoFY08"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# --- OLLAMA (Local) AYARLARI ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"

SUMMARY_SYSTEM_PROMPT = """Sen YönSis (Personel Yönetim Sistemi) için geliştirilmiş yapay zeka Kurumsal CTO Asistanı'sın (Jarvis).
Kişiliğin: Keskin, net, analitik ve saygılı. Sıkı bir askeri veya üst düzey yönetici asistanı disiplinine sahipsin.
ÖNEMLİ KURALLAR:
1. Klasik AI sohbet başlangıçlarından KESİNLİKLE kaçın. "Merhaba", "Selam", "Size sunmaktan memnuniyet duyarım" gibi laf kalabalığı yapma.
2. KESİN KURAL (HALLUCINATION YASAK): SANA VERİLEN 'System Data Result' İÇİNDEKİ SAYILARI BİREBİR KULLAN! Asla 181 kadrolu, 1 geçici gibi veride yazmayan detaylar UYDURMA. Veritabanından gelen metinde "182 kişi var" yazıyorsa sadece "182 kişi var" de. Olmayan departmanları listeleme.
3. Sana sağlanan sistem verilerinde gruplandırılma yapılmışsa, bu veriyi KESİNLİKLE Markdown formatında (```) temiz bir ASCII (*TABLO*) çizerek göster.
4. EĞER kullanıcı teknik olmayan veya yetki dışı bir soru soruyorsa "Bu komut YönSis veri kapsamı dışındadır." diyerek kestirip at. ANCAK 'System Data Result' içerisinde özellikle "Kullanıcı genel bir selamlama yaptı, kendini tanıt" gibi bir [SİSTEM NOTU] görüyorsan, o zaman "kapsam dışı" demek yerine, "Merhaba, ben Jarvis. YönSis yapay zeka asistanınızım. Size personel istatistikleri, dağılım ve arama konularında nasıl yardımcı olabilirim?" şeklinde kendini tanıt!
5. KESİN KURAL: SADECE eğer 'System Data Result' içinde mantıklı bir personel tablosu, liste veya kişi bilgisi başarıyla bulunmuşsa cevabının sonuna KESİNLİKLE "Dilerseniz bu veriyi Excel raporu olarak hazırlayabilirim." cümlesini ekle. Eğer veritabanı "Bulunamadı", "Hata", "0 kişi", "ulaşılamadı" gibisinden boş yanıt verdiyse Excel TEKLİF ETME!
Sana sağlanan JSON/METİN verisini analiz et ve komutanına/yöneticine bilgi verir gibi doğrudan, kaliteli bir şekilde formatla."""

INTENT_SYSTEM_PROMPT = """Sen Türkçe dilinde çalışan Niyet (Intent) Analizi motorusun.
Kullanıcının metnini ve önceki konuşma geçmişini okuyup SADECE JSON formatında çıktı üretmelisin. JSON dışında tek bir kelime dahi üretme.

[KABUL EDİLEN NİYETLER / İNTENTLER]:
1) general_chat (Kullanıcı "Selam", "Merhaba", "Sen kimsin", "Neler yapabilirsin" gibi sohbet ediyorsa. type: "chat", intent: "general_chat")
2) export_excel (Kullanıcı önceki sorgusunun sonucunu "Evet excel olarak ver / raporu indir" şeklinde İSTİYORSA bunu seç. Fakat İLK DEFA soruyorsa seçme. type: "action", intent: "export_excel")
3) database_query (Personel arama, sayma, gruplama, isim sorma, telefon sorma, birim dağılımı bulma vb. TÜM YönSis veritabanı sorguları için bunu kullan. type: "query")
   - 'filters': Django Personel modelindeki lookup'lar. Önceki konuşma bağlamı KESİNLİKLE dahil edilmelidir! (Örn: ad__icontains, soyad__icontains, cinsiyet__iexact, unvan__ad__icontains, brans__ad__icontains, kadrolu_personel (boolean olarak True/False. Geçici/Sözleşmeli olanlar için False kullan), ozel_durumu__ad__icontains, unvan_brans_eslestirme__kisa_unvan__ad__icontains, unvan_brans_eslestirme__kisa_unvan__ust_birim__ad__icontains, kurum__ad__icontains). "gecici__icontains" gibi sahte fieldlar YAZMA.
   - 'is_active': (Sadece 'Aktif' çalışanlar isteniyorsa True, 'ayrılanlar/pasifler' için False, hepsi veya belirtilmemişse null) Not: 'Geçici' durumu aktiflikle ilgili değildir, sadece kadrolu_personel=False ile bulunmalıdır!
   - 'group_by': (Dağılım veya gruplama yapılması istenen kolon: "unvan__ad", "brans__ad", "cinsiyet", "kadro_yeri__ad", vb. Dağılım yoksa null)
   - 'is_excel_export': (Eğer kullanıcı bu yeni aramayı direkt "excel tablosu olarak hazırla / excel olarak ver" diyorsa True, demiyorsa False)
   - 'explanation': Neden bu filtreleri ürettin?

[ÖRNEKLER]
Giriş: (Önceki mesaj: "Aktif uzman tabip sayımız nedir") -> Kullanıcı: "Geçici olan kim?"
Çıktı: {"type": "query", "intent": "database_query", "parameters": {"filters": {"unvan__ad__icontains": "Uzman Tabip", "kadrolu_personel": false}, "is_active": true, "group_by": null, "is_excel_export": false, "explanation": "Onceki baglamda aktif uzman tabipler konusuldu. Gecici demek kadrolu_personel=false demektir."}}

Giriş: "Ahmet Yılmaz'ın telefonu nedir?"
Çıktı: {"type": "query", "intent": "database_query", "parameters": {"filters": {"ad__icontains": "Ahmet", "soyad__icontains": "Yılmaz"}, "is_active": null, "group_by": null, "explanation": "Isim ve soyisim ile telefon sorgusu."}}

Giriş: "Selam Jarvis"
Çıktı: {"type": "chat", "intent": "general_chat", "parameters": {}}

Giriş: "engelli personellerin ünvanlarına göre dağılımı"
Çıktı: {"type": "query", "intent": "database_query", "parameters": {"filters": {"ozel_durumu__ad__icontains": "Engelli"}, "is_active": null, "group_by": "unvan__ad", "explanation": "Engelliler unvana gore gruplandi"}}
"""

def generate_jarvis_response(prompt):
    """Eski fonksiyon, artık doğrudan process_action üzerinden özetlenecek."""
    return summarize_data_with_llm(prompt, "Sistem bağlandı ancak yetki verisi yok.")

def detect_intent_with_llm(message, history=[]):
    if LLM_MODE == "online":
        return _detect_intent_gemini(message, history)
    else:
        return _detect_intent_ollama(message, history)

def summarize_data_with_llm(user_message, data_result, history=[]):
    if LLM_MODE == "online":
        return _summarize_data_gemini(user_message, data_result, history)
    else:
        return _summarize_data_ollama(user_message, data_result, history)

# ==========================================
# GEMINI (Online) FONKSİYONLARI
# ==========================================
def _build_gemini_contents(user_message, system_prompt_text, additional_context="", history=[]):
    # Gemini requires contents array: [{"role":..., "parts":[{"text":...}]}, ...]
    contents = []
    
    # Add history
    for msg in history:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg.get("text", "")}]
        })
        
    # Add current prompt
    current_prompt = f"{additional_context}\nKullanıcı: {user_message}"
    contents.append({
        "role": "user",
        "parts": [{"text": current_prompt}]
    })
    return contents

def _detect_intent_gemini(message, history=[]):
    headers = {"Content-Type": "application/json"}
    
    contents = _build_gemini_contents(message, INTENT_SYSTEM_PROMPT, "Şimdi bu soruya NİYET (INTENT) tespiti yapıp SADECE JSON CIKTISI dön:", history)
    
    payload = {
        "system_instruction": {"parts": [{"text": INTENT_SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1}
    }
    try:
        response = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        text_response = data.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "")
        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text_response)
    except Exception as e:
        print(f"[GEMINI] Intent Detection Hatası: {e}")
        return {"type": "out_of_scope"}

def _summarize_data_gemini(user_message, data_result, history=[]):
    headers = {"Content-Type": "application/json"}
    
    additional_context = f"Veritabanından Gelen Saf Veri (System Data Result): {data_result}\n\nYukarıdaki verilere göre, kullanıcının sorusuna uygun, resmi ve kısa bir cevap ver:"
    contents = _build_gemini_contents(user_message, SUMMARY_SYSTEM_PROMPT, additional_context, history)
    
    payload = {
        "system_instruction": {"parts": [{"text": SUMMARY_SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.7}
    }
    try:
        response = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "Sistemsel bir hata oluştu.")
    except Exception as e:
        print(f"[GEMINI] Özetleme Hatası: {e}")
        return "Yanıt işlenirken bir Google Gemini sorunu oluştu."

# ==========================================
# OLLAMA (Local) FONKSİYONLARI
# ==========================================
def _build_ollama_prompt(system_prompt, user_message, additional_context="", history=[]):
    prompt = f"System: {system_prompt}\n{additional_context}\n"
    for msg in history:
        role = "User" if msg.get("role") == "user" else "Jarvis"
        prompt += f"{role}: {msg.get('text', '')}\n"
    prompt += f"User: {user_message}\nJarvis:"
    return prompt

def _detect_intent_ollama(message, history=[]):
    headers = {"Content-Type": "application/json"}
    full_prompt = _build_ollama_prompt(INTENT_SYSTEM_PROMPT, message, "Şimdi bu soruya NİYET (INTENT) tespiti yapıp SADECE JSON CIKTISI dön:", history)
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "format": "json"
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json().get("response", "")
        match = re.search(r'\{.*\}', data, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(data)
    except Exception as e:
        print(f"[OLLAMA] Intent Detection Hatası: {e}")
        return {"type": "out_of_scope"}

def _summarize_data_ollama(user_message, data_result, history=[]):
    headers = {"Content-Type": "application/json"}
    
    additional_context = f"Veritabanından Gelen Saf Veri (System Data Result): {data_result}\n\nYukarıdaki verilere göre, kullanıcının sorusuna uygun, resmi ve kısa bir cevap ver:"
    full_prompt = _build_ollama_prompt(SUMMARY_SYSTEM_PROMPT, user_message, additional_context, history)
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json().get("response", "Sistemsel bir hata oluştu.")
    except Exception as e:
        print(f"[OLLAMA] Özetleme Hatası: {e}")
        return "Yanıt işlenirken Ollama bağlantı sorunu oluştu."

