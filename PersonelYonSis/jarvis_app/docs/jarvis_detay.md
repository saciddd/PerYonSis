# Jarvis AI - Uygulama ve Geliştirici Dokümantasyonu

## Genel Bakış
Jarvis, YönSis (Personel Yönetim Sistemi) için tasarlanmış kurumsal bir yapay zeka asistanıdır ("CTO Asistanı"). Rolü, kullanıcılardan gelen doğal dildeki soruları arka planda otomatik olarak veritabanı sorgularına çevirmek, personeller hakkında istatistik, listeleme veya kişi bulma işlemlerini yapıp kullanıcıya net ve rafine bir bilgi (Gerektiğinde Excel raporu) sunmaktır.

## Kullanılan Teknolojiler
- **Backend Framework:** Django (Sistem veritabanı ile ORM aracılığıyla bütünleşik)
- **Yapay Zeka (LLM) Sağlayıcıları:** 
  - **Local (Yerel):** Ollama (`gemma3:4b` modeli). Tamamen ücretsizdir, yerelde çalışır ve veriyi dışarı çıkarmaz ancak donanıma bağlıdır.
  - **Online (Bulut):** Google Gemini API (`gemini-2.5-flash` modeli). Hızlıdır, mantık kapasitesi daha yüksektir.
- **Veri Dışa Aktarımı:** `openpyxl` kütüphanesi (Excel formatlama).

## Sistemin Çalışma Mantığı (Akış)

Sistem modüler bir yapı izleyerek çalışmaktadır:

1. **Mesaj Karşılama (`api_chat` Görünümü):**
   Kullanıcının gönderdiği mesaj frontend tarafından (JS üzerinden HTTP POST ile) alınır ve action_engine sürecine gönderilir.

2. **Niyet Tespiti - Intent Detection (`llm_service.py`):**
   İlk adımda, kullanıcının ne istediğini çözmek adına yapay zeka bir "Niyet" analizi yapar. LLM, katı bir System Prompt yönlendirmesiyle sadece bir JSON döndürmeye zorlanır.
   - *Olası Niyetler:* `general_chat` (sohbet), `export_excel` (Excel indirme işlevi), `database_query` (veri arama durumu).
   - *Filtre Türetme:* `database_query` niyetinde, gelen metin incelenir ve `{"unvan__ad__icontains": "Uzman Tabip", "kadrolu_personel": false}` gibi spesifik Django ORM filtreleri çıkarılır.

3. **Veritabanı Araması (`capabilities/dynamic_search.py`):**
   AI'dan dönen filtre parametreleri (`filters`, `is_active`, `group_by` vs.) alınır ve doğrudan YönSis `Personel` modelinde sorgu (query) atılır.
   Bulunan personeller gerekirse Python düzeyinde aktif/pasif durumuyla (`durum` alanına göre) filtrelenir ve `group_by` değeri varsa (örnek: "unvan__ad") bu kırılıma göre gruplanır.
   Sorgulanan filtreleme aynı zamanda daha sonra kullanılabilecek ihtimal dahilinde `request.session['jarvis_last_search']` içerisine de kaydedilir (Excel vb. için).

4. **Metni Doğallaştırma - Summarization (`llm_service.py`):**
   Dinamik aramadan çıkan SAF veritabanı bulgusu (örneğin "Toplam Bulunan: 1, Ahmet Yılmaz - Ünvan: Tabip"), tekrar LLM'e gönderilir. Öncellikli kural **halüsinasyon yasağıdır** (veride olmayan bir şeyi ekleme yasağı). LLM, asistan kişiliğine bürünerek (resmi, direkt, net) veriyi Markdown kullanarak kullanıcı odaklı bir arayüz metnine dönüştürür.

5. **Excel Dışa Aktarımı (`views.py` / `export_excel_view`):**
   Kullanıcı raporu indirmek istediğinde Intent Engine bunu `export_excel` olarak işaretler ve UI üzerinden session'daki son arama veritabanında tekrar uygulanarak filtrelenen kişi listesinin `jarvis_personel_raporu.xlsx` olarak indirilmesi sağlanır.

## Beceriler ve Uygulama Yetenekleri
- **Personel Sorgulama & Analitik:** 
  Herhangi bir ünvan veya statüyle personel aranabilir ("Aktif kaç uzman hekimimiz var?", "Kadrolu olmayan geçici personeller listesi").
- **Kişi Temelli Yaklaşım:** 
  "Ahmet Yılmaz'ın departmanı ve telefonu nedir?" şeklindeki soruları anlayıp, veritabanındaki kişi kaydını tespit edip döndürür.
- **Gruplama (Kırılım Çıkarma):**
  Dağılım sorularında ("Engellilerin ünvanlara göre dağılımını göster" vb.), bilgileri tablo / madde imleri şeklinde gruplandırıp vererek analiz imkanı sunar.
- **Tabloyu Excele Çevirme:**
  Doğal diyalog esnasında "Bunu tablo olarak/excel olarak indir" talebini direkt kavrayarak indirme eylemini tetikler.
- **Güvenli Erişim:**
  Tüm işlemler `login_required` ile korunmakta ve LLM'e giden yetkiler sınırlıdır. Ayrıca asistan, YönSis dışı sorularda kapsam sınırının dışına çıkıldığında kullanıcıyı uyararak güvenli kullanım alanında kalır.
