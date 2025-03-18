from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
import calendar
from datetime import datetime
from .models import MesaiKontrol, Personel, Hizmet, Birim, PersonelBirim, Mesai, UserBirim  # Removed MesaiOnay
from PersonelYonSis.models import User
from django.db import models

def hizmet_tanimlari(request):
    hizmetler = Hizmet.objects.all()
    return render(request, 'hekim_cizelge/hizmet_tanimlari.html', {"hizmetler": hizmetler})

def add_hizmet(request):
    if request.method == 'POST':
        try:
            hizmet_name = request.POST.get('hizmet_name')
            hizmet_tipi = request.POST.get('hizmet_tipi')
            hafta_ici_suresi = request.POST.get('hizmet_suresi_hafta_ici')
            hafta_sonu_suresi = request.POST.get('hizmet_suresi_hafta_sonu')
            max_hekim = request.POST.get('max_hekim', 1)
            nobet_ertesi_izinli = bool(request.POST.get('nobet_ertesi_izinli'))

            # Süreleri dakikaya çevir (saat:dakika formatından)
            def sure_to_dakika(sure_str):
                if not sure_str:
                    return None
                saat, dakika = map(int, sure_str.split(':'))
                return saat * 60 + dakika

            hafta_ici_dakika = sure_to_dakika(hafta_ici_suresi)
            hafta_sonu_dakika = sure_to_dakika(hafta_sonu_suresi) if hafta_sonu_suresi else None

            if hafta_ici_dakika is None:
                raise ValueError("Hafta içi süresi gereklidir")

            Hizmet.objects.create(
                HizmetName=hizmet_name,
                HizmetTipi=hizmet_tipi,
                HizmetSuresiHaftaIci=hafta_ici_dakika,
                HizmetSuresiHaftaSonu=hafta_sonu_dakika,
                MaxHekimSayisi=max_hekim,
                NobetErtesiIzinli=nobet_ertesi_izinli
            )

            messages.success(request, "Hizmet başarıyla eklendi.")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Hizmet eklenirken bir hata oluştu: {str(e)}")

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
# Personel Adı, Unvanı, Branşı ve Çalıştığı Birim bilgilerini güncelleme işlemi
def personel_update(request):
    if request.method == 'POST':
        personel_id = request.POST.get('id')  # Formdan gelen personel ID'si
        birim_id = request.POST.get('birim')  # Formdan gelen birim ID'si
        personel_name = request.POST.get('name')  # Formdan gelen personel adı
        personel_title = request.POST.get('title')  # Formdan gelen personel unvanı
        personel_branch = request.POST.get('branch')  # Formdan gelen personel branşı

        # Modellerden ilgili kayıtları çekiyoruz
        personel = Personel.objects.get(PersonelID=personel_id)
        birim = Birim.objects.get(BirimID=birim_id)
        # PersonelAdi, PersonelUnvan, PersonelBranş, PersonelBirim bilgilerini güncelle
        personel.PersonelName = personel_name
        personel.PersonelTitle = personel_title
        personel.PersonelBranch = personel_branch
        personel.save()
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

# Düzenlenecek birim bilgilerini JSON olarak döndürüyoruz
def birim_duzenle_form(request, birim_id):
    birim = get_object_or_404(Birim, BirimID=birim_id)
    hizmetler = Hizmet.objects.all()
    birim_data = {
        'BirimID': birim.BirimID,
        'BirimAdi': birim.BirimAdi,
        'VarsayilanHizmetID': birim.VarsayilanHizmet.HizmetID,
        'DigerHizmetler': [hizmet.HizmetID for hizmet in birim.DigerHizmetler.all()]
    }
    return JsonResponse({'birim': birim_data, 'hizmetler': list(hizmetler.values())})

# Birim Düzenleme İşlemini Kaydetme
def birim_duzenle(request, birim_id):
    if request.method == 'POST':
        birim_adi = request.POST.get('birim_adi')
        varsayilan_hizmet_id = request.POST.get('varsayilan_hizmet')
        diger_hizmetler_ids = request.POST.getlist('diger_hizmetler')

        # VarsayilanHizmet ve diger_hizmetler kontrolü
        if not varsayilan_hizmet_id:
            messages.error(request, "Varsayılan hizmet seçilmelidir.")
            return redirect('hekim_cizelge:birim_duzenle_form', birim_id)
        
        if not birim_adi:
            messages.error(request, "Birim adı boş bırakılamaz.")
            return redirect('hekim_cizelge:birim_duzenle_form', birim_id)

        # birim düzenleme işlemi
        try:
            varsayilan_hizmet = Hizmet.objects.get(HizmetID=varsayilan_hizmet_id)
            birim = Birim.objects.get(BirimID=birim_id)
            birim.BirimAdi = birim_adi
            birim.VarsayilanHizmet = varsayilan_hizmet
            birim.save()

            # Diğer hizmetleri ManyToMany ilişkisinde ekleme
            if diger_hizmetler_ids:
                diger_hizmetler = Hizmet.objects.filter(HizmetID__in=diger_hizmetler_ids)
                birim.DigerHizmetler.set(diger_hizmetler)

            messages.success(request, "Birim başarıyla düzenlendi.")
        except Hizmet.DoesNotExist:
            messages.error(request, "Seçilen varsayılan hizmet bulunamadı.")
        except Exception as e:
            messages.error(request, f"Birim düzenlenirken bir hata oluştu: {str(e)}")

        return redirect('hekim_cizelge:birim_tanimlari')

def cizelge(request):
    current_year = int(request.GET.get('year', datetime.now().year))
    current_month = int(request.GET.get('month', datetime.now().month))

    # Günlerin tam tarihleri ve hafta sonu bilgilerini oluştur
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = [
        {
            'full_date': f"{current_year}-{current_month:02}-{day:02}",
            'day_num': day,
            'is_weekend': calendar.weekday(current_year, current_month, day) >= 5
        }
        for day in range(1, days_in_month + 1)
    ]

    # Kullanıcının yetkili olduğu birimleri al
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim', flat=True)
    birimler = Birim.objects.filter(BirimID__in=user_birimler)

    # Seçili birimdeki personelleri ve hizmetleri al
    selected_birim_id = request.GET.get('birim_id')
    if selected_birim_id:
        personeller = Personel.objects.filter(personelbirim__birim_id=selected_birim_id)
        selected_birim = Birim.objects.get(BirimID=selected_birim_id)
        hizmetler = list(selected_birim.DigerHizmetler.all()) + [selected_birim.VarsayilanHizmet]
    else:
        personeller = Personel.objects.none()
        hizmetler = []
        selected_birim = None

    # Mesai verilerini al ve tüm hizmet ilişkilerini prefetch et
    mesailer = Mesai.objects.filter(
        Personel__in=personeller,
        MesaiDate__year=current_year,
        MesaiDate__month=current_month
    ).select_related('Personel').prefetch_related(
        'Hizmetler'
    )

    # Personel bilgilerini ve JSON olarak tam mesai verilerini ekle
    personel_dict = {p.PersonelID: p.PersonelName for p in personeller}
    for personel in personeller:
        personel.mesai_data = []
        for mesai in mesailer.filter(Personel=personel):
            hizmet_list = []
            for hizmet in mesai.Hizmetler.all():
                hizmet_list.append({
                    'name': hizmet.HizmetName,
                    'type': hizmet.HizmetTipi,
                    'is_varsayilan': hizmet.HizmetID == selected_birim.VarsayilanHizmet.HizmetID
                })
            
            personel.mesai_data.append({
                'MesaiDate': mesai.MesaiDate.strftime("%Y-%m-%d"),
                'Hizmetler': hizmet_list,
                'OnayDurumu': mesai.OnayDurumu,
                'MesaiID': mesai.MesaiID
            })

    # Approval mode kontrolü
    is_approval_mode = request.GET.get('mode') == 'approval'
    
    context = {
        'personeller': personeller,
        'days': days,
        'birimler': birimler,
        'current_month': current_month,
        'current_year': current_year,
        'months': [{'value': i, 'label': calendar.month_name[i]} for i in range(1, 13)],
        'years': [year for year in range(current_year - 1, current_year + 2)],
        'hizmetler': hizmetler,
        'selected_birim': selected_birim,
        'is_approval_mode': is_approval_mode,
    }

    return render(request, 'hekim_cizelge/cizelge.html', context)

@csrf_exempt
def cizelge_kaydet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            changes = data.get('changes', {})
            deletion = data.get('deletion', {})

            for key, hizmetIDs in changes.items():
                personel_id, date = key.split('_')
                personel = Personel.objects.get(PersonelID=personel_id)
                
                # Hizmet çakışma kontrolü - varsayılan hizmet hariç
                for hizmet_id in hizmetIDs:
                    if str(hizmet_id) != str(personel.birim.first().VarsayilanHizmet.HizmetID):
                        mevcut_personel = Mesai.objects.filter(
                            MesaiDate=date,
                            Hizmetler__HizmetID=hizmet_id,
                            Personel__personelbirim__birim=personel.birim.first()
                        ).exclude(
                            Personel=personel
                        ).first()

                        if mevcut_personel:
                            raise ValueError(
                                f'Bu hizmet zaten {mevcut_personel.Personel.PersonelName} isimli personele tanımlanmış!'
                            )
                
                # Nöbet ertesi kontrolü
                if not MesaiKontrol.nobet_ertesi_kontrol(personel_id, date):
                    raise ValueError(f'Nöbet ertesi mesai girilemez!')

                # Mesai kaydını oluştur/güncelle
                mesai, created = Mesai.objects.get_or_create(
                    Personel=personel,
                    MesaiDate=date,
                    defaults={
                        'OnayDurumu': 0,
                        'Degisiklik': True
                    }
                )
                
                if not created:
                    mesai.OnayDurumu = 0
                    mesai.Degisiklik = True
                    mesai.save()
                
                hizmetler = Hizmet.objects.filter(HizmetID__in=hizmetIDs)
                mesai.Hizmetler.set(hizmetler)

            # Silme işlemleri
            for key in deletion.keys():
                personel_id, date = key.split('_')
                personel = Personel.objects.get(PersonelID=personel_id)
                Mesai.objects.filter(Personel=personel, MesaiDate=date).delete()

            return JsonResponse({'status': 'success'})

        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Beklenmeyen bir hata oluştu: {str(e)}'
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def mesai_onay(request, mesai_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mesai = get_object_or_404(Mesai, MesaiID=mesai_id)
            
            # Update Mesai object directly instead of creating MesaiOnay
            mesai.OnayDurumu = data.get('onay_durumu', 0)
            mesai.Onaylayan = request.user
            mesai.OnayTarihi = datetime.now()
            mesai.Degisiklik = False
            mesai.save()
            
            return JsonResponse({
                'status': 'success',
                'mesai_id': mesai_id
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

def mesai_onay_durumu(request, mesai_id):
    mesai = get_object_or_404(Mesai, MesaiID=mesai_id)
    return JsonResponse({
        'mesai_id': mesai_id,
        'onay_durumu': mesai.OnayDurumu,
        'onay_tarihi': mesai.OnayTarihi.isoformat() if mesai.OnayTarihi else None,
        'onaylayan': mesai.Onaylayan.username if mesai.Onaylayan else None
    })

def onay_bekleyen_mesailer(request):
    # Kullanıcının yetkili olduğu birimler
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim', flat=True)
    
    # Değişiklik olan ve onay bekleyen mesaileri birim bazlı grupla
    birimler = Birim.objects.filter(BirimID__in=user_birimler).annotate(
        bekleyen_mesai=models.Count(
            'personelbirim__personel__mesai',
            filter=models.Q(
                personelbirim__personel__mesai__OnayDurumu=0,
                personelbirim__personel__mesai__Degisiklik=True
            )
        )
    ).filter(bekleyen_mesai__gt=0)

    return render(request, 'hekim_cizelge/onay_bekleyen_mesailer.html', {
        'birimler': birimler
    })

@csrf_exempt
def toplu_onay(request, birim_id):
    if request.method == 'POST':
        try:
            mesailer = Mesai.objects.filter(
                Personel__personelbirim__birim_id=birim_id,
                OnayDurumu=0,
                Degisiklik=True
            )
            onay_sayisi = mesailer.count()
            
            mesailer.update(
                OnayDurumu=1,
                Onaylayan=request.user,
                OnayTarihi=datetime.now(),
                Degisiklik=False
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'{onay_sayisi} adet mesai onaylandı.'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
