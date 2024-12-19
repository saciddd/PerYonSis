from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
import calendar
from datetime import datetime
from .models import Personel, Hizmet, Birim, PersonelBirim, Mesai, UserBirim
from PersonelYonSis.models import User

def hizmet_tanimlari(request):
    hizmetler = Hizmet.objects.all()
    return render(request, 'hekim_cizelge/hizmet_tanimlari.html', {"hizmetler": hizmetler})

def add_hizmet(request):
    if request.method == 'POST':
        hizmet_name = request.POST.get('hizmet_name')
        hizmet_tipi = request.POST.get('hizmet_tipi')
        hizmet_suresi = request.POST.get('hizmet_suresi')

        if hizmet_name and hizmet_tipi and hizmet_suresi:
            try:
                # Süreyi timedelta formatına dönüştür
                hours, minutes, seconds = map(int, hizmet_suresi.split(':'))
                duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)

                # Hizmet oluştur
                Hizmet.objects.create(
                    HizmetName=hizmet_name,
                    HizmetTipi=hizmet_tipi,
                    HizmetSuresi=duration
                )
            except ValueError:
                # Süre formatı hatalı
                return render(request, 'hekim_cizelge/hizmet_tanimlari.html', {
                    "hata": "Süre formatı hatalı! (örn: 8:00:00)",
                    "hizmetler": Hizmet.objects.all()
                })

        return redirect('hekim_cizelge:hizmet_tanimlari')

    return redirect('hekim_cizelge:hizmet_tanimlari')

def personeller(request):
    personeller = Personel.objects.all()
    birimler = Birim.objects.all()

    # Personel ile birim bilgilerini eşleştiriyoruz
    personel_birimleri = PersonelBirim.objects.select_related('personel', 'birim')

    return render(request, 'hekim_cizelge/personeller.html', {
        'personeller': personeller,
        'birimler': birimler,
        'personel_birimleri': personel_birimleri
    })



# Personel Ekleme Formunu Geri Döndür
def personel_ekle_form(request):
    return render(request, 'hekim_cizelge/personel_ekle_form.html')
# Yeni Personel Ekleme İşlemi
def personel_ekle(request):
    if request.method == 'POST':
        # Form verilerini al
        personel_id = request.POST['PersonelID']
        personel_name = request.POST['PersonelName']
        personel_title = request.POST['PersonelTitle']
        personel_branch = request.POST['PersonelBranch']

        # Yeni personel kaydet
        personel = Personel(
            PersonelID=personel_id,
            PersonelName=personel_name,
            PersonelTitle=personel_title,
            PersonelBranch=personel_branch
        )
        personel.save()

        # Başarı mesajı ekleyebilirsiniz
        return redirect('hekim_cizelge:personeller')  # Personel listesine yönlendir
    return HttpResponse("Geçersiz istek", status=400)

def personel_update(request):
    if request.method == 'POST':
        personel_id = request.POST.get('id')  # Formdan gelen personel ID'si
        birim_id = request.POST.get('birim')  # Formdan gelen birim ID'si

        # Modellerden ilgili kayıtları çekiyoruz
        personel = Personel.objects.get(PersonelID=personel_id)
        birim = Birim.objects.get(BirimID=birim_id)

        # PersonelBirim kaydını güncelle veya oluştur
        personel_birim, created = PersonelBirim.objects.update_or_create(
            personel=personel,
            defaults={'birim': birim}
        )

        return JsonResponse({'status': 'success', 'birim_adi': birim.BirimAdi})
    return JsonResponse({'status': 'error', 'message': 'Hata oluştu.'})



def birim_tanimlari(request):
    birimler = Birim.objects.prefetch_related('DigerHizmetler').select_related('VarsayilanHizmet').all()
    hizmetler = Hizmet.objects.all()
    return render(request, 'hekim_cizelge/birim_tanimlari.html', {
        'birimler': birimler,
        'hizmetler': hizmetler
    })
def add_birim(request):
    if request.method == 'POST':
        birim_adi = request.POST.get('birim_adi')
        varsayilan_hizmet_id = request.POST.get('varsayilan_hizmet')
        diger_hizmetler_ids = request.POST.getlist('diger_hizmetler')

        # VarsayilanHizmet ve diger_hizmetler kontrolü
        if not varsayilan_hizmet_id:
            messages.error(request, "Varsayılan hizmet seçilmelidir.")
            return redirect('hekim_cizelge:birim_tanimlari')
        
        if not birim_adi:
            messages.error(request, "Birim adı boş bırakılamaz.")
            return redirect('hekim_cizelge:birim_tanimlari')

        # Yeni birim oluşturma
        try:
            varsayilan_hizmet = Hizmet.objects.get(HizmetID=varsayilan_hizmet_id)
            yeni_birim = Birim.objects.create(
                BirimAdi=birim_adi,
                VarsayilanHizmet=varsayilan_hizmet
            )

            # Diğer hizmetleri ManyToMany ilişkisinde ekleme
            if diger_hizmetler_ids:
                diger_hizmetler = Hizmet.objects.filter(HizmetID__in=diger_hizmetler_ids)
                yeni_birim.DigerHizmetler.set(diger_hizmetler)

            messages.success(request, "Birim başarıyla eklendi.")
        except Hizmet.DoesNotExist:
            messages.error(request, "Seçilen varsayılan hizmet bulunamadı.")
        except Exception as e:
            messages.error(request, f"Birim eklenirken bir hata oluştu: {str(e)}")

        return redirect('hekim_cizelge:birim_tanimlari')

    # GET isteği durumunda kullanıcı birim tanımlama sayfasına yönlendirilir
    return redirect('hekim_cizelge:birim_tanimlari')
def birim_yetkileri(request, user_id):
    user = get_object_or_404(User, UserID=user_id)

    if request.method == 'GET':
        # Kullanıcının yetkili olduğu birimler
        yetkili_birimler = UserBirim.objects.filter(user=user).select_related('birim')
        tum_birimler = Birim.objects.all()

        yetkili_birimler_list = [{'BirimID': b.birim.BirimID, 'BirimAdi': b.birim.BirimAdi} for b in yetkili_birimler]
        tum_birimler_list = [{'BirimID': b.BirimID, 'BirimAdi': b.BirimAdi} for b in tum_birimler]

        # Eğer yetkili birim yoksa bile boş liste döner
        return JsonResponse({
            'yetkili_birimler': yetkili_birimler_list,
            'tum_birimler': tum_birimler_list
        })

    elif request.method == 'POST':
        birim_id = request.POST.get('birim_id')
        is_add = request.POST.get('is_add')  # "true" veya "false"

        birim = get_object_or_404(Birim, BirimID=birim_id)

        if is_add == 'true':
            UserBirim.objects.get_or_create(user=user, birim=birim)
        elif is_add == 'false':
            UserBirim.objects.filter(user=user, birim=birim).delete()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


def cizelge(request):
    current_year = int(request.GET.get('year', datetime.now().year))
    current_month = int(request.GET.get('month', datetime.now().month))

    # Günleri oluştur
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = [{'full_date': f"{current_year}-{current_month:02}-{day:02}"} for day in range(1, days_in_month + 1)]

    # Tüm personelleri ve birimleri al
    personeller = Personel.objects.all()
    birimler = Birim.objects.all()

    context = {
        'personeller': personeller,
        'days': days,
        'birimler': birimler,
        'current_month': current_month,
        'current_year': current_year,
        'months': [{'value': i, 'label': calendar.month_name[i]} for i in range(1, 13)],
        'years': [year for year in range(2024, 2025)],
    }

    return render(request, 'hekim_cizelge/cizelge.html', context)

def get_hizmetler(request, birim_id):
    hizmetler = Hizmet.objects.filter(birim__BirimID=birim_id)
    hizmet_list = [{'id': hizmet.HizmetID, 'name': hizmet.HizmetName} for hizmet in hizmetler]
    return JsonResponse({'hizmetler': hizmet_list})

@csrf_exempt
def cizelge_kaydet(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        for key, hizmet_id in data.items():
            personel_id, date = key.split('_')
            personel = Personel.objects.get(PersonelID=personel_id)
            hizmet = Hizmet.objects.get(HizmetID=hizmet_id)
            mesai, created = Mesai.objects.get_or_create(
                Personel=personel,
                MesaiDate=date
            )
            mesai.Hizmetler.add(hizmet)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
