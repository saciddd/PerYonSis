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

SUMMARY_SYSTEM_PROMPT = """Sen YönSis isimli personel yönetim sistemi için geliştirilmiş kurumsal bir asistansın.
Sadece YönSis verileri ve personel yönetimi ile ilgili sorulara cevap verirsin.
Genel kültür, yazılım, politika, din, günlük sohbet gibi konulara cevap vermezsin.
Bu tür sorulara: 'Bu sistem yalnızca YönSis kapsamındaki işlemler için kullanılabilir.' cevabını verirsin.
Sana sağlanan JSON/METİN verilerini analiz edip kullanıcıya kısa ve net konuşarak cevap ver."""

INTENT_SYSTEM_PROMPT = """Sen Türkçe dilinde çalışan güçlü bir Niyet (Intent) Analizi motorusun.
Sana verilen kullanıcı metnini okuyup SADECE belirtilen JSON formatında çıktı üretmelisin. JSON dışında hiçbir metin, markdown (```json ...) falan döndürme.
Aşağıda YönSis sistemi tarafından desteklenen işlemleri görebilirsin. Kullanıcının niyeti bunlardan birine giriyorsa o tipi (`type`: "query") döndür. Başka bir konuysa ("Nasılsın", "Hava nasıl", "Sen kimsin") "out_of_scope" döndür.

[KABUL EDİLEN NİYETLER / İNTENTLER]:
1) get_person_department
   - Anlamı: Belirli bir kişinin hangi birimde/bölümde/departmanda çalıştığını soruyor.
   - Parametre zorunluluğu: 'name' (Örn: "Ahmet")

2) get_person_phone
   - Anlamı: Belirli bir personelin telefon numarasını, iletişim numarasını soruyor.
   - Parametre zorunluluğu: 'name'

3) count_by_title
   - Anlamı: Sistemde belirtilen bir ünvanda (örneğin Tıbbi sekreter, hekim, bilgisayar mühendisi, sağlık teknikeri vb.) toplam veya aktif kaç kişi olduğunu soruyor.
   - Parametre zorunluluğu: 'title_name' (Örn: "Tıbbi sekreter", "Kadın Doğum Uzmanı", "Doktor", "Hekim")

4) count_unit_personnel
   - Anlamı: Belirli bir birimde toplam veya aktif çalışan kaç kişi olduğunu soruyor.
   - Parametre zorunluluğu: 'unit_name' (Örn: "Acil servis", "Bilgi işlem")

[ÖRNEK GİRİŞ VE ÇIKTILAR]
Giriş: "Sacit'in telefon numarası kaç"
Çıktı: {"type": "query", "intent": "get_person_phone", "parameters": {"name": "Sacit"}}

Giriş: "Ahmet hangi birimde?"
Çıktı: {"type": "query", "intent": "get_person_department", "parameters": {"name": "Ahmet"}}

Giriş: "sistemde kaç tane doktor var şu anda aktif"
Çıktı: {"type": "query", "intent": "count_by_title", "parameters": {"title_name": "doktor"}}

Giriş: "Tıbbi sekreter sayısı kaçtır"
Çıktı: {"type": "query", "intent": "count_by_title", "parameters": {"title_name": "Tıbbi sekreter"}}

Giriş: "bilgi işlem biriminde kaç kişi var"
Çıktı: {"type": "query", "intent": "count_unit_personnel", "parameters": {"unit_name": "bilgi işlem"}}

Giriş: "Sen kimsin"
Çıktı: {"type": "out_of_scope"}
"""

def generate_jarvis_response(prompt):
    """Eski fonksiyon, artık doğrudan process_action üzerinden özetlenecek."""
    return summarize_data_with_llm(prompt, "Sistem bağlandı ancak yetki verisi yok.")

def detect_intent_with_llm(message):
    if LLM_MODE == "online":
        return _detect_intent_gemini(message)
    else:
        return _detect_intent_ollama(message)

def summarize_data_with_llm(user_message, data_result):
    if LLM_MODE == "online":
        return _summarize_data_gemini(user_message, data_result)
    else:
        return _summarize_data_ollama(user_message, data_result)

# ==========================================
# GEMINI (Online) FONKSİYONLARI
# ==========================================
def _detect_intent_gemini(message):
    headers = {"Content-Type": "application/json"}
    payload = {
        "system_instruction": {"parts": [{"text": INTENT_SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": f"Kullanıcı Mesajı: {message}\nJSON Çıktısı:"}]}],
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

def _summarize_data_gemini(user_message, data_result):
    headers = {"Content-Type": "application/json"}
    payload = {
        "system_instruction": {"parts": [{"text": SUMMARY_SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": f"Bulunan Veri (System Data Result): {data_result}\nKullanıcı Sorduğu Soru: {user_message}\nBuna göre uygun, resmi ve kısa bir cevap ver:"}]}],
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
def _detect_intent_ollama(message):
    headers = {"Content-Type": "application/json"}
    full_prompt = f"{INTENT_SYSTEM_PROMPT}\nKullanıcı Mesajı: {message}\nJSON Çıktısı:"
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

def _summarize_data_ollama(user_message, data_result):
    headers = {"Content-Type": "application/json"}
    full_prompt = f"System: {SUMMARY_SYSTEM_PROMPT}\nBulunan Veri: {data_result}\nUser: {user_message}\nJarvis:"
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

