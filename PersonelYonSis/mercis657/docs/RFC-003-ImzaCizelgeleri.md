🧾 RFC-002 — İmza Çizelgeleri Oluşturma ve Yazdırma Sistemi

Tarih: 2025-10-30
Hazırlayan: Sacit Polat
Uygulama: mercis657
Bağlı Olduğu Modül: Çizelge (cizelge.html)

🎯 Amaç

Personellerin bir aylık günlük imza çizelgelerini otomatik olarak hazırlayabilmek.
Bu çizelgeler, hastane idaresine sunulmak üzere PDF formatında oluşturulacaktır.
Her personel için bir sayfa oluşturulacak; PDF çıktısı imzalanabilir formatta olacaktır.

🧩 Genel Akış

1. Kullanıcı “İmza Çizelgeleri Yazdır” butonuna basar.
2. Ekrana bir SweetAlert2 modal açılır:
    “İlgili döneme ait İmza Çizelgeleri hazırlanacak. Mesai verileri olsun mu?”
    Seçenekler:
- ✅ Evet (mesai verileri dahil)
- ⚪ Hayır (boş mesai sütunları)
- ❌ İptal
3. Kullanıcı Evet veya Hayır seçerse:
- Mevcut çizelge listesindeki tüm personeller backend’e gönderilir.
- Django tarafında PDF oluşturma işlemi başlar.
- Her personel için tek sayfa hazırlanır.
- Sayfalar birleştirilerek çok sayfalı tek PDF oluşturulur.
4. PDF tarayıcıda yeni sekmede açılır.

🧱 Teknik Detaylar
1. Frontend Değişiklikleri (cizelge.html)
Yeni Buton:
<button id="imzaCizelgeleriBtn" class="btn btn-secondary ms-2">
  <i class="bi bi-printer"></i> İmza Çizelgeleri Yazdır
</button>

2. SweetAlert2 İletişimi:
document.getElementById("imzaCizelgeleriBtn").addEventListener("click", function() {
  Swal.fire({
    title: "İmza Çizelgeleri Hazırlansın mı?",
    text: "İlgili döneme ait İmza Çizelgeleri hazırlanacak. Mesai verileri olsun mu?",
    icon: "question",
    showCancelButton: true,
    confirmButtonText: "Evet, mesai verileriyle",
    cancelButtonText: "İptal",
    showDenyButton: true,
    denyButtonText: "Hayır, boş çizelge",
  }).then((result) => {
    if (result.isConfirmed || result.isDenied) {
      const includeMesai = result.isConfirmed;
      fetch(`/imza_cizelgeleri_yazdir/?mesai=${includeMesai}`)
        .then(res => res.blob())
        .then(blob => {
          const url = window.URL.createObjectURL(blob);
          window.open(url, "_blank");
        });
    }
  });
});

2. Backend Endpoint (views.py)
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage
import pdfkit
import calendar, io
from datetime import date
from .models import Personel, Mesai

# PDFKit yapılandırması
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

def imza_cizelgeleri_yazdir(request):
    include_mesai = request.GET.get("mesai", "false") == "true"

    # Dönem bilgilerini al (aktif çizelge sayfasındaki)
    current_year = int(request.GET.get("year"))
    current_month = int(request.GET.get("month"))
    birim = request.GET.get('birim') or ""
    liste = PersonelListesi.objects.get(birim=birim, yil=current_year, ay=current_month)


    # Header context
    try:
        file_url = f"file:///{staticfiles_storage.path('logo/kdh_logo.png')}"
    except Exception:
        file_url = None

    context_pdf = {
        'dokuman_kodu': 'KU.FR.06',
        'form_adi': 'Personel Günlük İmza Cetveli',
        'yayin_tarihi': 'Haziran 2018',
        'kurum': 'KAYSERİ DEVLET HASTANESİ',
        'revizyon_tarihi': 'Aralık 2018',
        'revizyon_no': '01',
        'sayfa_no': '1',
        'pdf_logo': file_url,
    }

    # Personelleri getir
    personeller = PersonelListesiKayit.objects.filter(liste=liste).select_related('personel').order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname')

    pages = []
    for personel in personeller:
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        days = [date(current_year, current_month, d) for d in range(1, days_in_month + 1)]

        mesai_data = {}
        if include_mesai:
            mesailer = Mesai.objects.filter(Personel=personel, MesaiDate__year=current_year, MesaiDate__month=current_month)
            for m in mesailer:
                mesai_data[m.MesaiDate.strftime('%Y-%m-%d')] = m.MesaiTanim.Saat if m.MesaiTanim else ""

        html_content = render_to_string("pdf_templates/imza_cizelgesi.html", {
            "personel": personel,
            "days": days,
            "mesai_data": mesai_data,
            **context_pdf
        })
        pages.append(html_content)

    # Pdf oluştur
    template = get_template('mercis657/pdf/calisma_listesi.html')
    html = template.render({ html_context })
    # PDF ayarları
    options = {
        'page-size': 'A4',
        'orientation': 'Portrait',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': '',
        'enable-external-links': True,
        'quiet': ''
    }

    # PDF oluştur
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)

    # HTTP response oluştur (open in new tab)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="imza_cizelgeleri_{current_year}_{current_month}.pdf"'
    return response

3. PDF Template (templates/mercis657/pdf/imza_cizelgesi.html)
{% load static %}
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <style>
    @page { size: A4 portrait; margin: 2cm 1cm; }
    table { border-collapse: collapse; width: 100%; font-size: 12px; }
    th, td { border: 1px solid #000; padding: 4px; text-align: center; }
    .header { text-align: center; margin-bottom: 10px; }
    .footer { margin-top: 30px; font-size: 11px; }
  </style>
</head>
<body>

<!-- Header -->
<div class="header">
  {% include "common/pdf_header_dikey.html" with kurum=kurum form_adi=form_adi dokuman_kodu=dokuman_kodu yayin_tarihi=yayin_tarihi revizyon_tarihi=revizyon_tarihi revizyon_no=revizyon_no sayfa_no=sayfa_no pdf_logo=pdf_logo %}
</div>

<p><b>AD / SOYAD:</b> {{ personel.PersonelName }} {{ personel.PersonelSurname }}<br>
<b>ÇALIŞTIĞI SERVİS:</b> {{ personel.birim.BirimAdi }} &nbsp;&nbsp;
<b>UNVAN:</b> {{ personel.PersonelTitle }} &nbsp;&nbsp;
<b>AİT OLDUĞU AY/YIL:</b> {{ days.0|date:"Y" }} - {{ days.0|date:"F" }}</p>

<table>
  <thead>
    <tr>
      <th>Tarih</th>
      <th>SABAH GELİŞ</th>
      <th>MESAİ</th>
      <th>AKŞAM ÇIKIŞ</th>
    </tr>
  </thead>
  <tbody>
    {% for day in days %}
    <tr {% if day|date:"w" in "0,6" %}style="background:#eee"{% endif %}>
      <td>{{ day|date:"j.m.Y" }}</td>
      <td></td>
      <td>{{ mesai_data.day|default:"" }}</td>
      <td></td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<div class="footer">
  <p>Kontrol Eden (Birim Sorumlusu) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Müdür Yardımcısı</p>
</div>

</body>
</html>

📦 Dosya Yapısı
- views klasöründe imza_cizelgeleri_views.py oluşturulacak.
- views klasöründe __init__.py güncellenecek.
- html şablon "mercis657/pdf" klasöründe olacak.

- url eklemesi:
urls.py → path("imza_cizelgeleri_yazdir/", views.imza_cizelgeleri_yazdir)