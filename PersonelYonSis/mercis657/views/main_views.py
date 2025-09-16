from io import BytesIO
import os
from django.db import IntegrityError
import pandas as pd
from openpyxl import load_workbook, Workbook
import calendar
from datetime import datetime, timedelta, date
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from PersonelYonSis import settings
from ..models import Birim, Mesai, Mesai_Tanimlari, Personel, PersonelListesi, PersonelListesiKayit, UserBirim, Kurum, UstBirim, Idareci, Izin, ResmiTatil
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import locale
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from ..valuelists import CKYS_BTF_VALUES
from ..forms import MesaiTanimForm, ResmiTatilForm
User = get_user_model()
try:
    # Windows için
    locale.setlocale(locale.LC_ALL, 'turkish')
except locale.Error:
    try:
        # Linux/Unix için
        locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    except locale.Error:
        # Hiçbiri çalışmazsa varsayılan locale kullan
        locale.setlocale(locale.LC_ALL, '')
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

@login_required
def cizelge(request):
    user = request.user
    user_birimler = UserBirim.objects.filter(user=user).select_related('birim')
    print(f"Kullanıcı: {user.Username}, Birimler: {[b.birim.BirimAdi for b in user_birimler]}")
    izinler = Izin.objects.all()
    kurumlar = Kurum.objects.all()
    print(f"Kurumlar: {kurumlar}")
    ust_birimler = UstBirim.objects.all()
    idareciler = Idareci.objects.all()
    # Dönemler: mevcut aydan 6 ay önce ile 2 ay sonrası arası
    today = date.today().replace(day=1)
    donemler = []
    for i in range(-6, 3):
        d = today + relativedelta(months=i)
        value = f"{d.year}/{d.month:02d}"
        label = value
        donemler.append({'value': value, 'label': label})

    selected_birim_id = request.GET.get('birim_id') or ""
    selected_donem = request.GET.get('donem') or ""
    pastcontext = {
            "user_birimler": user_birimler,
            "selected_birim_id": selected_birim_id,
            "donemler": donemler,
            "selected_donem": selected_donem,
            "mesai_options": Mesai_Tanimlari.objects.all(),
            "kurumlar": kurumlar,
            "ust_birimler": ust_birimler,
            "idareciler": idareciler,
            "izinler": izinler,
        }
    # Eğer GET ile birim ve dönem seçilmemişse, context'e sadece seçim listelerini gönder
    if not selected_birim_id or not selected_donem:
        return render(request, 'mercis657/cizelge.html', pastcontext)
    # Dönem bilgisini parse et ("YYYY/MM" formatı)
    try:
        current_year, current_month = map(int, selected_donem.split('/'))
    except Exception:
        messages.warning(request, "Geçersiz dönem formatı.")
        return render(request, 'mercis657/cizelge.html', pastcontext)

    birim_id = selected_birim_id

    if not birim_id:
        messages.warning(request, "Lütfen bir birim seçiniz.")
        return render(request, 'mercis657/cizelge.html', pastcontext)

    birim = get_object_or_404(Birim, BirimID=birim_id)

    if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
        return HttpResponseForbidden("Bu birim için yetkiniz yok.")

    # Liste varsa getir
    try:
        liste = PersonelListesi.objects.get(birim=birim, yil=current_year, ay=current_month)
    except PersonelListesi.DoesNotExist:
        messages.warning(request, f"{current_month}/{current_year} için personel listesi oluşturulmamış.")
        return render(request, 'mercis657/cizelge.html', pastcontext)

    personeller = Personel.objects.filter(personellistesikayit__liste=liste).distinct()
    mesai_tanimlari = Mesai_Tanimlari.objects.all()
    mesailer = Mesai.objects.filter(
        Personel__in=personeller,
        MesaiDate__year=current_year,
        MesaiDate__month=current_month
    ).select_related('MesaiTanim', 'Izin').prefetch_related('yedekler')

    # Resmi tatilleri al
    resmi_tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=current_year,
        TatilTarihi__month=current_month
    ).values_list('TatilTarihi', flat=True)
    
    # Gün listesi
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = [
        {
            'full_date': f"{current_year}-{current_month:02}-{day:02}",
            'day_num': day,
            'is_weekend': calendar.weekday(current_year, current_month, day) >= 5,
            'is_resmi_tatil': f"{current_year}-{current_month:02}-{day:02}" in [t.strftime('%Y-%m-%d') for t in resmi_tatiller]
        }
        for day in range(1, days_in_month + 1)
    ]

    # Personel mesai eşleme
    mesai_map = {}
    for mesai in mesailer:
        key = f"{mesai.Personel.PersonelID}_{mesai.MesaiDate.strftime('%Y-%m-%d')}"
        last_backup = mesai.yedekler.order_by('-created_at').first()
        mesai_map[key] = {
            "MesaiID": mesai.MesaiID,
            "MesaiTanimID": mesai.MesaiTanim.id if mesai.MesaiTanim else None,
            "MesaiTanimRenk": mesai.MesaiTanim.Renk if mesai.MesaiTanim else None,
            "IzinID": mesai.Izin.id if mesai.Izin else None,
            "Saat": mesai.MesaiTanim.Saat if mesai.MesaiTanim else "",
            "IzinAd": mesai.Izin.ad if mesai.Izin else "",
            "Degisiklik": mesai.Degisiklik,
            "PrevSaat": (last_backup.MesaiTanim.Saat if (last_backup and last_backup.MesaiTanim) else ""),
            "PrevIzinAd": (last_backup.Izin.ad if (last_backup and last_backup.Izin) else "")
        }

    # Personel nesnesine mesai bilgisi ekleyelim
    for p in personeller:
        p.mesai_data = []
        for day in days:
            key = f"{p.PersonelID}_{day['full_date']}"
            mesai_info = mesai_map.get(key, {
                "MesaiID": None,
                "MesaiTanimID": None,
                "IzinID": None,
                "Saat": "",
                "IzinAd": "",
                "Degisiklik": False,
                "PrevSaat": "",
                "PrevIzinAd": ""
            })
            mesai_info["MesaiDate"] = day['full_date']
            mesai_info["is_weekend"] = day['is_weekend']
            mesai_info["is_resmi_tatil"] = day['is_resmi_tatil']
            p.mesai_data.append(mesai_info)

    context = {
        "personeller": personeller,
        "mesai_options": mesai_tanimlari,
        "izinler": izinler,
        "days": days,
        "birim": birim,
        "current_year": current_year,
        "current_month": current_month,
        "months": [{'value': i, 'label': calendar.month_name[i]} for i in range(1, 13)],
        "years": [year for year in range(2023, 2027)],
        "user_birimler": user_birimler,
        "selected_birim_id": selected_birim_id,
        "liste": liste.id if liste else 0,
        "donemler": donemler,
        "selected_donem": selected_donem,
        "kurumlar": kurumlar,
        "ust_birimler": ust_birimler,
        "idareciler": idareciler,
    }
    return render(request, 'mercis657/cizelge.html', context)

@login_required
def personel_listeleri(request):
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim_id', flat=True)
    birimler = Birim.objects.filter(id__in=user_birimler)
    listeler = PersonelListesi.objects.filter(birim__in=birimler).order_by('-yil', '-ay')
    return render(request, 'mercis657/personel_listeleri.html', {
        'birimler': birimler,
        'listeler': listeler
    })

@login_required
def personel_listesi_olustur(request):
    if request.method == 'POST':
        birim_id = request.POST.get('birim_id')
        yil = int(request.POST.get('yil'))
        ay = int(request.POST.get('ay'))

        birim = get_object_or_404(Birim, id=birim_id)

        if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
            return HttpResponseForbidden('Bu birim için yetkiniz yok.')

        try:
            liste, created = PersonelListesi.objects.get_or_create(birim=birim, yil=yil, ay=ay)
            if created:
                messages.success(request, 'Personel listesi oluşturuldu.')
            else:
                messages.warning(request, 'Bu ay ve birim için liste zaten var.')
        except IntegrityError:
            messages.error(request, 'Liste oluşturulurken bir hata oluştu.')

        return redirect('mercis657:personel_listeleri')

@login_required
def personel_listesi_detay(request, liste_id):
    liste = get_object_or_404(PersonelListesi, id=liste_id)

    if not UserBirim.objects.filter(user=request.user, birim=liste.birim).exists():
        return HttpResponseForbidden('Bu listeye erişim yetkiniz yok.')

    mevcut_personeller = PersonelListesiKayit.objects.filter(personel_listesi=liste).select_related('personel')
    tum_personeller = Personel.objects.all().order_by('FirstName', 'LastName')

    return render(request, 'mercis657/personel_listesi_detay.html', {
        'liste': liste,
        'mevcut_personeller': mevcut_personeller,
        'tum_personeller': tum_personeller
    })

@login_required
def personel_ekle_listeye(request, liste_id):
    if request.method == 'POST':
        liste = get_object_or_404(PersonelListesi, id=liste_id)

        if not UserBirim.objects.filter(user=request.user, birim=liste.birim).exists():
            return HttpResponseForbidden('Bu listeye erişim yetkiniz yok.')

        personel_id = request.POST.get('personel_id')
        personel = get_object_or_404(Personel, PersonelID=personel_id)

        kayit, created = PersonelListesiKayit.objects.get_or_create(
            personel_listesi=liste,
            personel=personel
        )

        if created:
            messages.success(request, 'Personel listeye eklendi.')
        else:
            messages.warning(request, 'Bu personel zaten listede.')

        return redirect('mercis657:personel_listesi_detay', liste_id=liste.id)

@login_required
def personel_kaldir_liste(request, liste_id, kayit_id):
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    kayit = get_object_or_404(PersonelListesiKayit, id=kayit_id, personel_listesi=liste)

    if not UserBirim.objects.filter(user=request.user, birim=liste.birim).exists():
        return HttpResponseForbidden('Bu listeye erişim yetkiniz yok.')

    kayit.delete()
    messages.success(request, 'Personel listeden kaldırıldı.')
    return redirect('mercis657:personel_listesi_detay', liste_id=liste.id)

@login_required
def personel_cikar(request, liste_id, personel_id):
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    if not UserBirim.objects.filter(user=request.user, birim=liste.birim).exists():
        messages.warning(request, 'Yetkisiz işlem.')
        return redirect('mercis657:personel_listeleri')

    kayit = get_object_or_404(PersonelListesiKayit, liste=liste, personel_id=personel_id)
    kayit.delete()
    messages.success(request, 'Personel listeden çıkarıldı.')
    return redirect('mercis657:personel_listesi_detay', liste_id=liste.id)

@csrf_exempt
def birim_yetki_ekle(request, birim_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user = User.objects.get(Username=username)
            birim = Birim.objects.get(pk=birim_id)
            obj, created = UserBirim.objects.get_or_create(user=user, birim=birim)
            if created:
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error", "message": "Kullanıcı zaten yetkili."})
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı."})
        except Birim.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Birim bulunamadı."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Geçersiz istek."})

@login_required
def tanimlamalar(request):
    kurumlar = Kurum.objects.all()
    ust_birimler = UstBirim.objects.all()
    idareciler = Idareci.objects.all()
    izinler = Izin.objects.all()
    mesai_tanimlari = Mesai_Tanimlari.objects.all().order_by('Saat')
    mesai_form = MesaiTanimForm()
    resmi_tatil_form = ResmiTatilForm()
    return render(request, "mercis657/tanimlamalar.html", {
        "kurumlar": kurumlar,
        "ust_birimler": ust_birimler,
        "idareciler": idareciler,
        "izinler": izinler,
        "mesai_tanimlari": mesai_tanimlari,
        "form": mesai_form,
        "rt_form": resmi_tatil_form,
    })