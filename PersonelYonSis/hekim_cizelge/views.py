from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
import calendar
from datetime import datetime

from hekim_cizelge.forms import BildirimForm
from hekim_cizelge.utils import hesapla_fazla_mesai, hesapla_icap_suresi
from .models import Bildirim, Izin, MesaiKontrol, Personel, Hizmet, Birim, PersonelBirim, Mesai, ResmiTatil, UserBirim  # Removed MesaiOnay
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

    # GET isteği durumunda kullanıcı birim tanımlama sayfasına yönlendirilirr
    return redirect('hekim_cizelge:birim_tanimlari')
def birim_yetkileri(request, user_id):
    user = get_object_or_404(User, UserID=user_id)

    if request.method == 'GET':
        yetkili_birimler = UserBirim.objects.filter(user=user).select_related('birim')
        tum_birimler = Birim.objects.all()

        yetkili_birimler_list = [{'BirimID': b.birim.BirimID, 'BirimAdi': b.birim.BirimAdi} for b in yetkili_birimler]
        tum_birimler_list = [{'BirimID': b.BirimID, 'BirimAdi': b.BirimAdi} for b in tum_birimler]

        return JsonResponse({
            'yetkili_birimler': yetkili_birimler_list,
            'tum_birimler': tum_birimler_list
        })

    elif request.method == 'POST':
        birim_id = request.POST.get('birim_id')
        is_add = request.POST.get('is_add')

        birim = get_object_or_404(Birim, BirimID=birim_id)

        if is_add == 'true':
            UserBirim.objects.get_or_create(user=user, birim=birim)
        elif is_add == 'false':
            UserBirim.objects.filter(user=user, birim=birim).delete()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

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

def birim_duzenle(request, birim_id):
    if request.method == 'POST':
        birim_adi = request.POST.get('birim_adi')
        varsayilan_hizmet_id = request.POST.get('varsayilan_hizmet')
        diger_hizmetler_ids = request.POST.getlist('diger_hizmetler')

        if not varsayilan_hizmet_id:
            messages.error(request, "Varsayılan hizmet seçilmelidir.")
            return redirect('hekim_cizelge:birim_duzenle_form', birim_id)
        
        if not birim_adi:
            messages.error(request, "Birim adı boş bırakılamaz.")
            return redirect('hekim_cizelge:birim_duzenle_form', birim_id)

        try:
            varsayilan_hizmet = Hizmet.objects.get(HizmetID=varsayilan_hizmet_id)
            birim = Birim.objects.get(BirimID=birim_id)
            birim.BirimAdi = birim_adi
            birim.VarsayilanHizmet = varsayilan_hizmet
            birim.save()

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

    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = [
        {
            'full_date': f"{current_year}-{current_month:02}-{day:02}",
            'day_num': day,
            'is_weekend': calendar.weekday(current_year, current_month, day) >= 5
        }
        for day in range(1, days_in_month + 1)
    ]

    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim', flat=True)
    birimler = Birim.objects.filter(BirimID__in=user_birimler)

    selected_birim_id = request.GET.get('birim_id')
    if selected_birim_id:
        personeller = Personel.objects.filter(personelbirim__birim_id=selected_birim_id)
        selected_birim = Birim.objects.get(BirimID=selected_birim_id)
        hizmetler = list(selected_birim.DigerHizmetler.all()) + [selected_birim.VarsayilanHizmet]
    else:
        personeller = Personel.objects.none()
        hizmetler = []
        selected_birim = None

    mesailer = Mesai.objects.filter(
        Personel__in=personeller,
        MesaiDate__year=current_year,
        MesaiDate__month=current_month
    ).select_related('Personel', 'Izin').prefetch_related(
        'Hizmetler'
    )

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
            
            mesai_data = {
                'MesaiDate': mesai.MesaiDate.strftime("%Y-%m-%d"),
                'Hizmetler': hizmet_list,
                'OnayDurumu': mesai.OnayDurumu,
                'MesaiID': mesai.MesaiID
            }

            if mesai.Izin:
                mesai_data['Izin'] = {
                    'id': mesai.Izin.IzinID,
                    'tip': mesai.Izin.IzinTipi,
                    'renk': mesai.Izin.IzinRenk
                }
            
            personel.mesai_data.append(mesai_data)

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
        'izinler': Izin.objects.all(),
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

            for key, value in changes.items():
                personel_id, date = key.split('_')
                personel = Personel.objects.get(PersonelID=personel_id)
                
                if value.get('type') == 'hizmet':
                    # Hizmet kombinasyonunu kontrol ett
                    hizmetler = Hizmet.objects.filter(HizmetID__in=value.get('hizmetler', []))
                    is_valid, errors = MesaiKontrol.validate_hizmet_combination(hizmetler)
                    
                    if not is_valid:
                        return JsonResponse({
                            'status': 'error',
                            'message': '\n'.join(errors)
                        })

                mesai, created = Mesai.objects.get_or_create(
                    Personel=personel,
                    MesaiDate=date,
                    defaults={
                        'OnayDurumu': 0,
                        'Degisiklik': True,
                        'SilindiMi': False
                    }
                )

                if not created:
                    mesai.OnayDurumu = 0
                    mesai.Degisiklik = True
                    mesai.save()

                if value.get('type') == 'clear':
                    mesai.Hizmetler.clear()
                    mesai.Izin = None
                    mesai.save()
                elif value.get('type') == 'hizmet':
                    mesai.Izin = None
                    mesai.save()
                    # Buradaki hatayı düzelttim - parantezleri kaldırdımm
                    hizmetler = Hizmet.objects.filter(HizmetID__in=value.get('hizmetler', []))
                    mesai.Hizmetler.set(hizmetler)
                elif value.get('type') == 'izin':
                    mesai.Hizmetler.clear()
                    if value.get('izin'):
                        izin = Izin.objects.get(IzinID=value.get('izin'))
                        mesai.Izin = izin
                    else:
                        mesai.Izin = None
                    mesai.save()

            return JsonResponse({'status': 'success'})
        except ValueError as e:
            return JsonResponse({
                'status': 'error', 
                'message': f'Veri format hatası: {str(e)}'
            })
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
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim', flat=True)
    
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

@csrf_exempt
def auto_fill_default(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            year = int(data.get('year'))
            month = int(data.get('month'))
            birim_id = data.get('birim_id')

            birim = Birim.objects.get(BirimID=birim_id)
            personeller = Personel.objects.filter(personelbirim__birim=birim)
            
            days_in_month = calendar.monthrange(year, month)[1]
            dates = [
                datetime(year, month, day) 
                for day in range(1, days_in_month + 1)
                if calendar.weekday(year, month, day) < 5
            ]

            count = 0
            for personel in personeller:
                for date in dates:
                    current_date = date.date()
                    
                    prev_date = current_date - timedelta(days=1)
                    
                    has_previous_nobet = Mesai.objects.filter(
                        Personel=personel,
                        MesaiDate=prev_date,
                        Hizmetler__HizmetTipi='Nöbet',
                        Hizmetler__NobetErtesiIzinli=True,
                        SilindiMi=False
                    ).exists()
                    
                    if has_previous_nobet:
                        continue
                    
                    mesai = Mesai.objects.filter(
                        Personel=personel,
                        MesaiDate=current_date
                    ).first()

                    if not mesai:
                        mesai = Mesai.objects.create(
                            Personel=personel,
                            MesaiDate=current_date,
                            OnayDurumu=0,
                            Degisiklik=True,
                            SilindiMi=False
                        )
                        mesai.Hizmetler.add(birim.VarsayilanHizmet)
                        count += 1
                    elif mesai.SilindiMi or not mesai.Hizmetler.exists():
                        mesai.SilindiMi = False
                        mesai.OnayDurumu = 0
                        mesai.Degisiklik = True
                        mesai.save()
                        mesai.Hizmetler.clear()
                        mesai.Hizmetler.add(birim.VarsayilanHizmet)
                        count += 1

            return JsonResponse({
                'status': 'success',
                'count': count,
                'message': f'{count} adet varsayılan hizmet eklendi.'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def bildirimler(request):
    current_year = int(request.GET.get('year', datetime.now().year))
    current_month = int(request.GET.get('month', datetime.now().month))
    current_mode = request.GET.get('mode', 'MESAI')  # MESAI veya ICAP

    # Yetkili olunan birimleri all
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim', flat=True)
    birimler = Birim.objects.filter(BirimID__in=user_birimler)

    # Seçili birimi al
    selected_birim_id = request.GET.get('birim_id')
    selected_birim = None
    personeller = None
    bildirimler = None

    if selected_birim_id:
        selected_birim = get_object_or_404(Birim, BirimID=selected_birim_id)
        personeller = Personel.objects.filter(personelbirim__birim=selected_birim)
        
        donem = datetime(current_year, current_month, 1).date()
        bildirimler = Bildirim.objects.filter(
            PersonelBirim__birim=selected_birim,
            DonemBaslangic=donem,
            BildirimTipi=current_mode,
            SilindiMi=False
        ).select_related('Personel', 'PersonelBirim')

    # Ay içindeki günleri hesapla
    days = []
    if selected_birim_id:
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        days = [
            {
                'day_num': day,
                'is_weekend': calendar.weekday(current_year, current_month, day) >= 5,
                'is_holiday': ResmiTatil.objects.filter(
                    TatilTarihi=datetime(current_year, current_month, day).date()
                ).exists()
            }
            for day in range(1, days_in_month + 1)
        ]

    context = {
        'current_year': current_year,
        'current_month': current_month,
        'current_mode': current_mode,
        'birimler': birimler,
        'selected_birim': selected_birim,
        'personeller': personeller,
        'bildirimler': bildirimler,
        'months': [{'value': i, 'label': calendar.month_name[i]} for i in range(1, 13)],
        'years': range(current_year - 1, current_year + 2),
        'days': days,
    }

    return render(request, 'hekim_cizelge/bildirimler.html', context)

@csrf_exempt 
def bildirim_olustur(request, tip):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            personel_id = data.get('personel_id')
            birim_id = data.get('birim_id')
            donem = datetime.strptime(data.get('donem'), '%Y-%m').date()

            # PersonelBirim kaydını al
            personel_birim = get_object_or_404(
                PersonelBirim, 
                personel_id=personel_id, # personel_id yerine personel
                birim_id=birim_id     # birim_id yerine birim
            )

            # Mevcut bildirimi kontrol et veya yeni oluştur
            bildirim, created = Bildirim.objects.get_or_create(
                PersonelBirim=personel_birim,
                DonemBaslangic=donem,
                BildirimTipi=tip,
                defaults={
                    'OlusturanKullanici': request.user
                }
            )

            # Süreleri hesapla ve güncelle
            if tip == 'MESAI':
                mesai_detay = hesapla_fazla_mesai(personel_id, donem)
                bildirim.NormalFazlaMesai = mesai_detay['normal']
                bildirim.BayramFazlaMesai = mesai_detay['bayram']
                bildirim.RiskliNormalFazlaMesai = mesai_detay['riskli_normal']
                bildirim.RiskliBayramFazlaMesai = mesai_detay['riskli_bayram']
                bildirim.MesaiDetay = mesai_detay['gunluk_detay']
            else:
                icap_detay = hesapla_icap_suresi(personel_id, donem)
                bildirim.NormalIcap = icap_detay['normal']
                bildirim.BayramIcap = icap_detay['bayram']
                bildirim.IcapDetay = icap_detay['gunluk_detay']

            bildirim.save()

            # Yanıt verisi hazırla
            response_data = {
                'status': 'success',
                'bildirim_id': bildirim.BildirimID,
                'bildirim_data': {
                    'normal_mesai': float(bildirim.NormalFazlaMesai),
                    'bayram_mesai': float(bildirim.BayramFazlaMesai),
                    'riskli_normal': float(bildirim.RiskliNormalFazlaMesai),
                    'riskli_bayram': float(bildirim.RiskliBayramFazlaMesai),
                    'normal_icap': float(bildirim.NormalIcap),
                    'bayram_icap': float(bildirim.BayramIcap),
                    'toplam_mesai': float(bildirim.ToplamFazlaMesai),
                    'toplam_icap': float(bildirim.ToplamIcap)
                }
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def bildirim_toplu_olustur(request, birim_id):
    """Birim personellerinin tümü için bildirim oluşturur"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            year = int(data.get('year'))
            month = int(data.get('month'))
            tip = data.get('tip')
            
            birim = get_object_or_404(Birim, BirimID=birim_id)
            personeller = Personel.objects.filter(personelbirim__birim=birim)
            count = 0

            donem = datetime(year, month, 1).date()
            for personel in personeller:
                personel_birim = PersonelBirim.objects.get(personel=personel, birim=birim)
                
                # Mevcut bildirim kontrolü
                bildirim = Bildirim.objects.filter(
                    PersonelBirim=personel_birim,
                    DonemBaslangic=donem,
                    BildirimTipi=tip,
                    SilindiMi=False
                ).first()

                if not bildirim:
                    bildirim = Bildirim(
                        PersonelBirim=personel_birim,
                        DonemBaslangic=donem,
                        BildirimTipi=tip,
                        OlusturanKullanici=request.user
                    )
                    
                    if tip == 'MESAI':
                        mesai_detay = hesapla_fazla_mesai(personel.PersonelID, donem)
                        bildirim.NormalFazlaMesai = mesai_detay['normal']
                        bildirim.BayramFazlaMesai = mesai_detay['bayram']
                        bildirim.RiskliNormalFazlaMesai = mesai_detay['riskli_normal']
                        bildirim.RiskliBayramFazlaMesai = mesai_detay['riskli_bayram']
                        bildirim.MesaiDetay = mesai_detay['gunluk_detay']
                    else:
                        icap_detay = hesapla_icap_suresi(personel.PersonelID, donem)
                        bildirim.NormalIcap = icap_detay['normal']
                        bildirim.BayramIcap = icap_detay['bayram']
                        bildirim.IcapDetay = icap_detay['gunluk_detay']
                        
                    bildirim.save()
                    count += 1

            return JsonResponse({
                'status': 'success',
                'count': count
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def bildirim_form(request, bildirim_id):
    """Bildirim formunu PDF olarak oluşturur"""
    try:
        bildirim = get_object_or_404(Bildirim, BildirimID=bildirim_id)
        
        # PDF oluştur
        pdf = BildirimForm.create_pdf(bildirim)
        
        # Dosya adını oluştur
        filename = f'bildirim_{bildirim.BildirimTipi}_{bildirim.DonemBaslangic.strftime("%Y%m")}_{bildirim.Personel.PersonelID}.pdf'
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.write(pdf)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Form oluşturulurken hata: {str(e)}')
        return redirect('hekim_cizelge:bildirimler')

@csrf_exempt
def bildirim_listele(request, yil, ay, birim_id):
    """Birime ait bildirimleri listeler"""
    try:
        donem = datetime(yil, ay, 1).date()
        bildirimler = Bildirim.objects.filter(
            PersonelBirim__birim_id=birim_id,
            DonemBaslangic=donem,
            SilindiMi=False
        ).select_related(
            'PersonelBirim__personel'
        )
        
        data = []
        for bildirim in bildirimler:
            item = {
                'id': bildirim.BildirimID,
                'personel_id': bildirim.PersonelBirim.personel.PersonelID,
                'personel': bildirim.PersonelBirim.personel.PersonelName,
                'tip': bildirim.BildirimTipi,
                'normal_mesai': float(bildirim.NormalFazlaMesai),
                'bayram_mesai': float(bildirim.BayramFazlaMesai),
                'riskli_normal': float(bildirim.RiskliNormalFazlaMesai),
                'riskli_bayram': float(bildirim.RiskliBayramFazlaMesai),
                'normal_icap': float(bildirim.NormalIcap),
                'bayram_icap': float(bildirim.BayramIcap),
                'toplam_mesai': float(bildirim.ToplamFazlaMesai),
                'toplam_icap': float(bildirim.ToplamIcap),
                'onay_durumu': bildirim.OnayDurumu,
                'MesaiDetay': bildirim.MesaiDetay,
                'IcapDetay': bildirim.IcapDetay
            }
            data.append(item)
            
        return JsonResponse({'status': 'success', 'data': data})
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@csrf_exempt
def bildirim_guncelle(request, bildirim_id):
    """Bildirim detaylarını günceller"""
    if request.method == 'POST':
        try:
            bildirim = get_object_or_404(Bildirim, BildirimID=bildirim_id)
            
            # Onaylı bildirimleri güncelleme
            if bildirim.OnayDurumu == 1:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Onaylanmış bildirimler güncellenemez'
                })
            
            data = json.loads(request.body)
            donem = datetime.strptime(data.get('donem'), '%Y-%m').date()
            
            # Bildirim tipine göre hesaplama yap
            if bildirim.BildirimTipi == 'MESAI':
                mesai_detay = hesapla_fazla_mesai(bildirim.Personel.PersonelID, donem)
                bildirim.NormalFazlaMesai = mesai_detay['normal']  
                bildirim.BayramFazlaMesai = mesai_detay['bayram']
                bildirim.RiskliNormalFazlaMesai = mesai_detay['riskli_normal']
                bildirim.RiskliBayramFazlaMesai = mesai_detay['riskli_bayram']
                bildirim.MesaiDetay = mesai_detay['gunluk_detay']
            else:
                icap_detay = hesapla_icap_suresi(bildirim.Personel.PersonelID, donem)
                bildirim.NormalIcap = icap_detay['normal']
                bildirim.BayramIcap = icap_detay['bayram']
                bildirim.IcapDetay = icap_detay['gunluk_detay']
            
            bildirim.save()
            
            return JsonResponse({
                'status': 'success',
                'bildirim_id': bildirim.BildirimID
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def bildirim_sil(request, bildirim_id):
    """Bildirimi soft-delete yapar"""
    if request.method == 'POST':
        try:
            bildirim = get_object_or_404(Bildirim, BildirimID=bildirim_id)
            
            # Onaylı bildirimleri silme
            if bildirim.OnayDurumu == 1:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Onaylanmış bildirimler silinemez'
                })
            
            bildirim.SilindiMi = True
            bildirim.save()
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt 
def bildirim_toplu_onay(request, birim_id):
    """Birime ait bildirimleri toplu onaylar/onaylarını kaldırır"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            year = int(data.get('year'))
            month = int(data.get('month'))
            tip = data.get('tip')
            onay_durumu = int(data.get('onay_durumu'))
            
            donem = datetime(year, month, 1).date()
            
            # Filtre kriterlerini güncelle
            filtre = {
                'PersonelBirim__birim_id': birim_id,
                'DonemBaslangic': donem,
                'BildirimTipi': tip,
                'SilindiMi': False
            }
            
            # Onay durumuna göre filtreleme (onay için 0, onay kaldırma için 1)
            if onay_durumu == 1:
                filtre['OnayDurumu'] = 0
            else:
                filtre['OnayDurumu'] = 1
            
            bildirimler = Bildirim.objects.filter(**filtre)
            islem_sayisi = bildirimler.count()
            
            if islem_sayisi == 0:
                mesaj = 'Onaylanacak bildirim bulunamadı.' if onay_durumu == 1 else 'Onayı kaldırılacak bildirim bulunamadı.'
                return JsonResponse({
                    'status': 'error',
                    'message': mesaj
                })
            
            # Bildirimleri güncelle
            bildirimler.update(
                OnayDurumu=onay_durumu,
                OnaylayanKullanici=request.user if onay_durumu == 1 else None,
                OnayTarihi=datetime.now() if onay_durumu == 1 else None
            )
            
            mesaj = f'{islem_sayisi} adet bildirim onaylandı.' if onay_durumu == 1 else f'{islem_sayisi} adet bildirimin onayı kaldırıldı.'
            
            return JsonResponse({
                'status': 'success',
                'count': islem_sayisi,
                'message': mesaj
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def resmi_tatiller(request):
    tatiller = ResmiTatil.objects.all().order_by('TatilTarihi')
    return render(request, 'hekim_cizelge/resmi_tatiller.html', {
        'tatiller': tatiller
    })

@csrf_exempt
def tatil_ekle(request):
    if request.method == 'POST':
        try:
            tarih = request.POST.get('tarih')
            aciklama = request.POST.get('aciklama')
            tip = request.POST.get('tip')

            ResmiTatil.objects.create(
                TatilTarihi=tarih,
                Aciklama=aciklama,
                TatilTipi=tip
            )
            messages.success(request, "Resmi tatil başarıyla eklendi.")
        except Exception as e:
            messages.error(request, f"Hata oluştu: {str(e)}")
            
    return redirect('hekim_cizelge:resmi_tatiller')

@csrf_exempt
def tatil_sil(request, tatil_id):
    """Resmi tatil kaydını siler"""
    if request.method == 'POST':
        try:
            tatil = get_object_or_404(ResmiTatil, TatilID=tatil_id)
            tatil.delete()
            messages.success(request, "Resmi tatil başarıyla silindi.")
        except Exception as e:
            messages.error(request, f"Silme işlemi başarısız: {str(e)}")
            
        return redirect('hekim_cizelge:resmi_tatiller')
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
