from io import BytesIO
import os
import pandas as pd
from openpyxl import load_workbook
import calendar
from datetime import datetime, timedelta
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from PersonelYonSis import settings
from .models import Mesai, Mesai_Tanimlari, Personel
import locale

locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')  # Türkçe ayarlayın

import os
import pandas as pd
from openpyxl import load_workbook, Workbook
from django.http import HttpResponse
from io import BytesIO
from django.conf import settings

def excel_export(request):
    current_year = int(request.GET.get('year', datetime.now().year))
    current_month = int(request.GET.get('month', datetime.now().month))

    df = pd.DataFrame(columns=["Personel Adı", "Personel Unvanı"])

    personeller = Personel.objects.all()
    mesailer = Mesai.objects.filter(MesaiDate__year=current_year, MesaiDate__month=current_month)

    rows = []
    for personel in personeller:
        personel.mesai_data = mesailer.filter(Personel=personel)
        row = {
            "Personel Adı": personel.PersonelName,
            "Personel Unvanı": personel.PersonelTitle
        }
        for mesai in personel.mesai_data:
            row[mesai.MesaiDate.strftime("%Y-%m-%d")] = mesai.MesaiData
        rows.append(row)

    df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

    template_path = os.path.join(settings.STATIC_ROOT, 'excels', 'cizelgeSablon1.xlsx')
    
    with BytesIO() as buffer:
        try:
            if os.path.exists(template_path):
                # Şablon varsa yükle
                book = load_workbook(template_path)
            else:
                # Şablon yoksa yeni bir Workbook oluştur
                book = Workbook()

            # Çalışma sayfası olup olmadığını kontrol et
            if not book.worksheets:
                book.create_sheet(title="Mesai Verileri")

            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                writer.book = book
                writer.sheets = {ws.title: ws for ws in book.worksheets}

                # Veriyi A2 hücresinden itibaren yazdır
                df.to_excel(writer, index=False, startrow=1, sheet_name='Mesai Verileri')

                # Başlık ekle
                sheet = writer.sheets['Mesai Verileri']
                sheet['A1'] = f"{current_year} - {current_month} dönemi Mesai verileri"

            # Yazdırma işlemi
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{current_year}_{current_month}_mesai_verileri.xlsx"'
            return response

        except Exception as e:
            return HttpResponse(f"Hata oluştu: {str(e)}", status=500)


def cizelge(request):
    current_year = int(request.GET.get('year', datetime.now().year))
    current_month = int(request.GET.get('month', datetime.now().month))

    # Günleri ve personel mesai verilerini getir
    days_in_month = calendar.monthrange(current_year, current_month)[1]

    # Günlerin tam tarihleri ve hafta sonu olup olmadığını içeren liste oluştur
    days = [{
        'full_date': f"{current_year}-{current_month:02}-{day:02}",
        'day_num': day,
        'is_weekend': calendar.weekday(current_year, current_month, day) >= 5
    } for day in range(1, days_in_month + 1)]

    # Tüm personeller ve ilgili ay için mesai verileri
    personeller = Personel.objects.all()
    mesai_tanimlari = Mesai_Tanimlari.objects.all()
    mesailer = Mesai.objects.filter(MesaiDate__year=current_year, MesaiDate__month=current_month)

    # Mesaileri personellere göre gruplandırma
    for personel in personeller:
        personel.mesai_data = [
            {
                'MesaiDate': mesai.MesaiDate.strftime("%Y-%m-%d"),
                'MesaiTanimSaat': mesai.MesaiTanim.Saat if mesai.MesaiTanim else ''
            }
            for mesai in mesailer.filter(Personel=personel)
        ]

    context = {
        'personeller': personeller,
        'days': days,  # Günler ve hafta sonu bilgileri
        'mesai_options': mesai_tanimlari,
        'current_month': current_month,
        'current_year': current_year,
        'months': [{'value': i, 'label': calendar.month_name[i]} for i in range(1, 13)],  # Aylar
        'years': [year for year in range(2024, 2025)],  # İstediğin yıl aralığı
    }

    return render(request, 'cizelge.html', context)


def cizelge_kaydet(request):
    if request.method == 'POST':
        changes = json.loads(request.body)
        for key, mesai_tanim_id in changes.items():
            personel_id, mesai_date = key.split('_')
            mesai_date = datetime.strptime(mesai_date, "%Y-%m-%d").date()
            
            Mesai.objects.update_or_create(
                Personel_id=personel_id,
                MesaiDate=mesai_date,
                defaults={'MesaiTanim_id': mesai_tanim_id}
            )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)


def personeller(request):
    personeller = Personel.objects.all()
    return render(request, 'personeller.html', {"personeller": personeller})
# Personel Ekleme Formunu Geri Döndür
def personel_ekle_form(request):
    return render(request, 'personel_ekle_form.html')

# Yeni Personel Ekleme İşlemi
def personel_ekle(request):
    if request.method == 'POST':
        # Form verilerini al
        personel_id = request.POST['PersonelID']
        personel_name = request.POST['PersonelName']
        personel_title = request.POST['PersonelTitle']
        birth_date = request.POST['BirthDate']

        # Yeni personel kaydet
        personel = Personel(
            PersonelID=personel_id,
            PersonelName=personel_name,
            PersonelTitle=personel_title,
            BirthDate=birth_date
        )
        personel.save()

        # Başarı mesajı ekleyebilirsiniz
        return redirect('mercis657:personeller')  # Personel listesine yönlendir
    return HttpResponse("Geçersiz istek", status=400)
def personel_update(request):
    if request.method == 'POST':
        personel_id = request.POST.get('id')
        personel_name = request.POST.get('name')
        personel_title = request.POST.get('title')

        # Personeli bul
        personel = get_object_or_404(Personel, PersonelID=personel_id)
        
        # Güncellenen alanlar
        personel.PersonelName = personel_name
        personel.PersonelTitle = personel_title
        personel.save()  # Değişiklikleri kaydet
        
        return JsonResponse({'status': 'success'})  # Başarı mesajı

    return JsonResponse({'status': 'error'})  # Hatalı durum
def mesai_tanimlari(request):
    mesai_tanimlari = Mesai_Tanimlari.objects.all()
    return render(request, 'mesai_tanimlari.html', {"mesai_tanimlari": mesai_tanimlari})
# Yeni Mesai Tanımı Ekleme Fonksiyonu
def add_mesai_tanim(request):
    if request.method == 'POST':
        # Formdan gelen verileri alıyoruz
        saat = request.POST.get('Saat')
        gunduz_mesaisi = request.POST.get('GunduzMesaisi') == 'on'
        aksam_mesaisi = request.POST.get('AksamMesaisi') == 'on'
        gece_mesaisi = request.POST.get('GeceMesaisi') == 'on'
        ise_geldi = request.POST.get('IseGeldi') == 'on'
        sonraki_gune_sarkiyor = request.POST.get('SonrakiGuneSarkiyor') == 'on'
        ara_dinlenme = request.POST.get('AraDinlenme')
        gecerli_mesai = request.POST.get('GecerliMesai') == 'on'
        ckys_btf_karsiligi = request.POST.get('CKYS_BTF_Karsiligi')

        # Ara dinlenme süresini timedelta nesnesine dönüştürme
        if ara_dinlenme:
            hours, minutes = map(int, ara_dinlenme.split(':'))
            ara_dinlenme_td = timedelta(hours=hours, minutes=minutes)
        else:
            ara_dinlenme_td = None

        # Yeni mesai tanımı oluşturma
        yeni_mesai = Mesai_Tanimlari(
            Saat=saat,
            GunduzMesaisi=gunduz_mesaisi,
            AksamMesaisi=aksam_mesaisi,
            GeceMesaisi=gece_mesaisi,
            IseGeldi=ise_geldi,
            SonrakiGuneSarkiyor=sonraki_gune_sarkiyor,
            AraDinlenme=ara_dinlenme_td,
            GecerliMesai=gecerli_mesai,
            CKYS_BTF_Karsiligi=ckys_btf_karsiligi
        )
        
        # Mesai süresini hesaplayarak kaydet
        yeni_mesai.calculate_sure()
        yeni_mesai.save()

        return redirect('mercis657:mesai_tanimlari')  # İşlem tamamlandığında liste sayfasına yönlendirme

    return render(request, 'mesai_tanimlari.html')

def mesai_tanim_update(request):
    mesai_id = request.POST.get('mesai_id')
    mesai = get_object_or_404(Mesai_Tanimlari, id=mesai_id)
    
    if request.method == 'POST':
        try:
            # Formdan gelen güncellenmiş verileri alıyoruz
            mesai.Saat = request.POST.get('saat')
            mesai.GunduzMesaisi = request.POST.get('GunduzMesaisi') == 'on'
            mesai.AksamMesaisi = request.POST.get('AksamMesaisi') == 'on'
            mesai.GeceMesaisi = request.POST.get('GeceMesaisi') == 'on'
            mesai.IseGeldi = request.POST.get('IseGeldi') == 'on'
            mesai.SonrakiGuneSarkiyor = request.POST.get('SonrakiGuneSarkiyor') == 'on'
            ara_dinlenme = request.POST.get('AraDinlenme')
            mesai.AraDinlenme = ara_dinlenme if ara_dinlenme else None
            mesai.GecerliMesai = request.POST.get('GecerliMesai') == 'on'
            mesai.CKYS_BTF_Karsiligi = request.POST.get('CKYS_BTF_Karsiligi')

            mesai.save()  # Güncellenmiş verileri kaydet
            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})
def delete_mesai_tanim(request):
    if request.method == 'POST':
        mesai_id = request.POST.get('mesai_id')
        try:
            mesai = get_object_or_404(Mesai_Tanimlari, id=mesai_id)
            mesai.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})