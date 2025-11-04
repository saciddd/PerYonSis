🧩 RFC-005-PersonelYonetimi.md

Başlık: Personel Yönetimi Ekranı
Uygulama: mercis657
Tarih: 2025-11-04
Hazırlayan: Sacit Polat

🎯 Amaç

Sistemdeki tüm personelleri tek ekranda sorgulayıp görüntülemek, geçmiş çalışma listelerine erişmek ve ilgili döneme ait çizelgeye yönlenebilmek.

🧱 İlgili Modeller

Personel

🔹 PersonelTCKN
🔹 PersonelName
🔹 PersonelSurname
🔹 PersonelTitle

PersonelListesiKayit

🔹 liste → FK → PersonelListesi
🔹 personel → FK → Personel

PersonelListesi

🔹 birim → FK → Birim
🔹 yil, ay

Birim

🔹 BirimID, BirimAdi

🧭 Sayfa: personel_yonetim.html
1️⃣ Filtre Alanı (üst kısım)

Form elemanları:

Ad Soyad
T.C. Kimlik No

Dönem (Yıl / Ay)
🔹 Sorgu butonu → fetch isteği ile tabloyu yeniler.

2️⃣ Sonuç Tablosu (alt kısım)

Kolonlar:

T.C. Kimlik No	Ad Soyad	Unvan	En Son Bulunduğu Liste	İşlemler
11111111111	Ali KAYA	Doktor	2025/11 – Dahiliye	[Listeler]

“En Son Bulunduğu Liste” bilgisi:

latest_liste = PersonelListesiKayit.objects.filter(personel=p).order_by('-liste__yil', '-liste__ay').first()


Şu biçimde gösterilir:
{{ latest_liste.liste.yil }}/{{ latest_liste.liste.ay }} - {{ latest_liste.liste.birim.BirimAdi }}

3️⃣ Modal: Personelin Listeleri

Trigger:

<button class="btn btn-outline-primary btn-sm" onclick="openPersonelListeleriModal({{ personel.PersonelID }})">
  <i class="bi bi-card-list"></i> Listeler
</button>


Modal İçeriği:

Tablo: Yıl / Ay, Birim, Listeye Git

Sıralama: Yeni → Eski

Buton örneği:

<a href="{% url 'mercis657:cizelge' %}?birim_id={{ row.birim.BirimID }}&donem={{ row.liste.yil }}/{{ row.liste.ay }}" 
   class="btn btn-sm btn-primary">Listeye Git</a>


Backend Endpoint:
/mercis657/personel/<id>/listeler/ → JSON döner:

[
  {"yil": 2025, "ay": 11, "birim": "İnsan Kaynakları", "birim_id": 3},
  {"yil": 2025, "ay": 10, "birim": "Yazı İşleri", "birim_id": 2}
]

⚙️ Backend Akışı
Fonksiyon	Açıklama
def personel_yonetim(request)	Sayfayı render eder.
def personel_sorgula(request)	Filtre kriterlerine göre personel listesini döner (JSON).
def personel_listeleri(request, personel_id)	Personelin geçmiş listelerini getirir.
🧠 Yetki & Güvenlik

Tüm endpointler:

if not request.user.has_permission('ÇS 657 Personel Yönetimi'):
    return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

📊 Geliştirme Notları

Tabloda DataTables veya AdminLTE grid kullanılabilir.
Modal dinamik olarak JS ile doldurulmalı.
Fetch sonrası SweetAlert ile geri bildirim verilebilir.