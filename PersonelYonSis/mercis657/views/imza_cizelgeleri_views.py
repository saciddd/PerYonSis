from datetime import date
import calendar
import io

from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage

import pdfkit

from mercis657.models import PersonelListesi, PersonelListesiKayit, Mesai, Birim


# PDFKit yapılandırması (Windows varsayılan kurulum yolu)
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')


def imza_cizelgeleri_yazdir(request):
    include_mesai = request.GET.get("mesai", "false") == "true"

    try:
        current_year = int(request.GET.get("year"))
        current_month = int(request.GET.get("month"))
    except Exception:
        return HttpResponseBadRequest("Geçersiz yıl/ay")

    birim_id = request.GET.get('birim')
    if not birim_id:
        return HttpResponseBadRequest("birim parametresi zorunludur")

    try:
        liste = PersonelListesi.objects.get(birim_id=birim_id, yil=current_year, ay=current_month)
    except PersonelListesi.DoesNotExist:
        return HttpResponseBadRequest("İstenen dönem ve birim için PersonelListesi bulunamadı")

    # Logo ve üstbilgi
    try:
        file_url = f"file:///{staticfiles_storage.path('logo/kdh_logo.png')}"
    except Exception:
        file_url = None

    header_ctx = {
        'dokuman_kodu': 'KU.FR.06',
        'form_adi': 'Personel Günlük İmza Cetveli',
        'yayin_tarihi': 'Haziran 2018',
        'kurum': 'KAYSERİ DEVLET HASTANESİ',
        'revizyon_tarihi': 'Aralık 2018',
        'revizyon_no': '01',
        'sayfa_no': '1',
        'pdf_logo': file_url,
    }

    # Günler
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = [date(current_year, current_month, d) for d in range(1, days_in_month + 1)]
    birim = Birim.objects.get(BirimID=birim_id)

    # Personeller
    kayitlar = (
        PersonelListesiKayit.objects
        .filter(liste=liste)
        .select_related('personel')
        .order_by('sira_no', 'personel__PersonelName', 'personel__PersonelSurname')
    )

    pages = []
    for kayit in kayitlar:
        mesai_data = {}
        if include_mesai:
            mesailer = Mesai.objects.filter(Personel=kayit.personel, MesaiDate__year=current_year, MesaiDate__month=current_month).select_related('MesaiTanim')
            for m in mesailer:
                key = m.MesaiDate.strftime('%Y-%m-%d')
                mesai_data[key] = m.MesaiTanim.Saat if m.MesaiTanim else ""

        html_content = render_to_string("mercis657/pdf/imza_cizelgesi.html", {
            "personel": kayit.personel,
            "days": days,
            "mesai_data": mesai_data,
            "birim": birim,
            **header_ctx
        })
        pages.append(html_content)

    # Sayfaları sayfa kırımı ile birleştir (her personel ayrı A4)
    page_break = '<div style="page-break-after: always;"></div>'
    full_html = page_break.join(pages)

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

    pdf = pdfkit.from_string(full_html, False, options=options, configuration=config)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="imza_cizelgeleri_{current_year}_{current_month}.pdf"'
    return response


