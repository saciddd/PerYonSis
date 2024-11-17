from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

from .models import Personel, Hizmet, Birim

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
    return render(request, 'hekim_cizelge/personeller.html', {"personeller": personeller})

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
        personel_id = request.POST.get('id')
        personel_name = request.POST.get('name')
        personel_title = request.POST.get('title')
        personel_branch = request.POST.get('branch')

        # Personeli bul
        personel = get_object_or_404(Personel, PersonelID=personel_id)
        
        # Güncellenen alanlar
        personel.PersonelName = personel_name
        personel.PersonelTitle = personel_title
        personel.PersonelBranch = personel_branch
        personel.save()  # Değişiklikleri kaydet
        
        return JsonResponse({'status': 'success'})  # Başarı mesajı

    return JsonResponse({'status': 'error'})  # Hatalı durum

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


def cizelge(request):
    return render(request, 'hekim_cizelge/cizelge.html')