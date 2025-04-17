from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Birim, HizmetSunumAlani, UserBirim, HizmetSunumCalismasi, Personel
from django.views.decorators.csrf import csrf_exempt
import json
import calendar

@login_required
def bildirim(request):
    # Kullanıcının yetkili olduğu birimleri getir 
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim', flat=True)
    birimler = Birim.objects.filter(BirimId__in=user_birimler)
    hsa_listesi = HizmetSunumAlani.objects.all()

    context = {
        'birimler': birimler,
        'hsa_listesi': hsa_listesi,
    }
    return render(request, 'hizmet_sunum_app/bildirim.html', context)

@login_required
def birim_detay(request, birim_id):
    birim = get_object_or_404(Birim, BirimId=birim_id)
    if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'})
    
    return JsonResponse({
        'BirimId': birim.BirimId,
        'BirimAdi': birim.BirimAdi,
        'KurumAdi': birim.KurumAdi,
        'HSAKodu': birim.HSAKodu.AlanKodu
    })

@csrf_exempt
@login_required
def birim_ekle(request):
    if request.method == 'POST':
        try:
            birim = Birim.objects.create(
                BirimAdi=request.POST['birimAdi'],
                KurumAdi=request.POST['kurumAdi'],
                HSAKodu=HizmetSunumAlani.objects.get(AlanKodu=request.POST['hsaKodu'])
            )
            
            # UserBirim kaydı oluştur
            UserBirim.objects.create(user=request.user, birim=birim)
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@login_required
def birim_guncelle(request, birim_id):
    birim = get_object_or_404(Birim, BirimId=birim_id)
    if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'})
    
    if request.method == 'POST':
        try:
            birim.BirimAdi = request.POST['birimAdi']
            birim.KurumAdi = request.POST['kurumAdi']
            birim.HSAKodu = HizmetSunumAlani.objects.get(AlanKodu=request.POST['hsaKodu'])
            birim.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def onceki_donem_personel(request, donem, birim_id):
    """Bir önceki döneme ait personelleri getir"""
    try:
        donem_date = datetime.strptime(donem, '%Y-%m')
        # Bir önceki ayı hesapla
        if donem_date.month == 1:
            onceki_ay = datetime(donem_date.year - 1, 12, 1)
        else:
            onceki_ay = datetime(donem_date.year, donem_date.month - 1, 1)
            
        # Önceki dönem personellerini getir
        personeller = HizmetSunumCalismasi.objects.filter(
            CalisilanBirimId_id=birim_id,
            Donem=onceki_ay.date()
        ).select_related('PersonelId').values(
            'PersonelId__PersonelId',
            'PersonelId__PersonelAdi',
            'PersonelId__PersonelSoyadi'
        ).distinct()
        
        data = [{
            'personel_id': p['PersonelId__PersonelId'],
            'tc_kimlik': '', # Bu alan şu an için boş bırakılıyor
            'adi': p['PersonelId__PersonelAdi'],
            'soyadi': p['PersonelId__PersonelSoyadi']
        } for p in personeller]
        
        return JsonResponse({'status': 'success', 'data': data})
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def get_birim_personelleri(request, birim_id, donem):
    """Bir önceki döneme ait personelleri getir"""
    try:
        # Dönem string'ini datetime objesine çevir
        donem_date = datetime.strptime(donem, '%Y-%m')
        
        # Önceki ayı hesapla
        if donem_date.month == 1:
            onceki_ay = datetime(donem_date.year - 1, 12, 1)
        else:
            onceki_ay = datetime(donem_date.year, donem_date.month - 1, 1)
            
        # Önceki dönem personellerini getir
        personeller = HizmetSunumCalismasi.objects.filter(
            CalisilanBirimId=birim_id,
            Donem=onceki_ay.date()
        ).select_related('PersonelId')
        
        data = [{
            'id': p.PersonelId.PersonelId,
            'tc_kimlik': p.PersonelId.TCKimlikNo,
            'adi': p.PersonelId.Adi,
            'soyadi': p.PersonelId.Soyadi,
            'baslangic': p.HizmetBaslangicTarihi.strftime('%Y-%m-%d'),
            'bitis': p.HizmetBitisTarihi.strftime('%Y-%m-%d'),
            'sorumlu': p.Sorumlu,
            'sertifika': p.Sertifika
        } for p in personeller]
        
        return JsonResponse({'status': 'success', 'data': data})
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@csrf_exempt
@login_required
def personel_kaydet(request):
    """Personel kayıtlarını oluştur"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            donem = datetime.strptime(data['donem'], '%Y-%m')
            birim_id = data['birim_id']
            personeller = data['personeller']

            # Dönem başlangıç ve bitiş tarihleri
            baslangic = donem.replace(day=1)
            bitis = donem.replace(day=calendar.monthrange(donem.year, donem.month)[1])

            # Seçili birimin AlanKodu'sunu al
            birim = Birim.objects.get(BirimId=birim_id)
            alan_kodu = birim.HSAKodu.AlanKodu

            for personel_data in personeller:
                tc_kimlik = personel_data.get('tc_kimlik', '').strip()
                adi = personel_data.get('adi', '').strip()
                soyadi = personel_data.get('soyadi', '').strip()
                if not tc_kimlik or not adi or not soyadi:
                    continue

                personel, _ = Personel.objects.get_or_create(
                    TCKimlikNo=tc_kimlik,
                    defaults={
                        'PersonelAdi': adi,
                        'PersonelSoyadi': soyadi
                    }
                )
                # Eğer isim/soyisim değişmişse güncelle
                if personel.PersonelAdi != adi or personel.PersonelSoyadi != soyadi:
                    personel.PersonelAdi = adi
                    personel.PersonelSoyadi = soyadi
                    personel.save()

                HizmetSunumCalismasi.objects.create(
                    PersonelId=personel,
                    CalisilanBirimId=birim,
                    Donem=baslangic.date(),
                    HizmetBaslangicTarihi=baslangic.date(),
                    HizmetBitisTarihi=bitis.date(),
                    CreatedBy=request.user,
                    OzelAlanKodu=alan_kodu
                )

            return JsonResponse({
                'status': 'success',
                'message': f'{len(personeller)} personel kaydı oluşturuldu.'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def bildirimler_listele(request, year, month, birim_id):
    """
    Seçili yıl, ay ve birim için bildirimleri JSON olarak döndürür.
    """
    try:
        from datetime import datetime
        donem = datetime(year, month, 1).date()
        bildirimler = HizmetSunumCalismasi.objects.filter(
            CalisilanBirimId__BirimId=birim_id,
            Donem=donem
        ).select_related('PersonelId')

        data = []
        for idx, b in enumerate(bildirimler, 1):
            data.append({
                'id': b.CalismaId,
                'tc_kimlik_no': getattr(b.PersonelId, 'TCKimlikNo', ''),
                'ad': b.PersonelId.PersonelAdi if hasattr(b.PersonelId, 'PersonelAdi') else '',
                'soyad': b.PersonelId.PersonelSoyadi if hasattr(b.PersonelId, 'PersonelSoyadi') else '',
                'baslangic': b.HizmetBaslangicTarihi.strftime('%Y-%m-%d') if b.HizmetBaslangicTarihi else '',
                'bitis': b.HizmetBitisTarihi.strftime('%Y-%m-%d') if b.HizmetBitisTarihi else '',
                'ozel_alan_kodu': '',  # Eğer modelde varsa ekleyin
                'sorumlu': b.Sorumlu,
                'sertifika': b.Sertifika,
                'kesinlesmis': b.Kesinlestirme,
            })

        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
