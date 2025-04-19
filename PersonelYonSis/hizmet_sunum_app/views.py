from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from datetime import datetime, date
from .models import Birim, HizmetSunumAlani, UserBirim, HizmetSunumCalismasi, Personel
import json
import calendar
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

@login_required
def bildirim(request):
    # Kullanıcının yetkili olduğu birimleri getir 
    user_birimler_qs = UserBirim.objects.filter(user=request.user).select_related('birim', 'birim__HSAKodu')
    birimler = [ub.birim for ub in user_birimler_qs]

    # Tüm HSA listesini modal için alalım
    hsa_listesi = HizmetSunumAlani.objects.all().order_by('AlanAdi')

    # Başlangıçta context'e seçili birim veya bildirim eklemeye gerek yok,
    # bu bilgiler AJAX ile yüklenecek.
    context = {
        'birimler': birimler,
        'hsa_listesi': hsa_listesi,
        # 'donemler' frontend JS ile oluşturuluyor, Django context'ine gerek yok.
    }
    return render(request, 'hizmet_sunum_app/bildirim.html', context)

@login_required
@require_GET
def birim_detay(request, birim_id):
    # Kullanıcının bu birime yetkisi var mı kontrol et
    if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
        
    birim = get_object_or_404(Birim.objects.select_related('HSAKodu'), BirimId=birim_id)
    
    # Frontend'in beklediği formatta döndür
    data = {
        'BirimId': birim.BirimId,
        'BirimAdi': birim.BirimAdi,
        'KurumAdi': birim.KurumAdi,
        'HSAKodu': birim.HSAKodu.AlanKodu if birim.HSAKodu else None,
        'HSAAdi': birim.HSAKodu.AlanAdi if birim.HSAKodu else None
    }
    return JsonResponse({'status': 'success', 'data': data})

@login_required
@require_POST
def birim_ekle(request):
    try:
        birim_adi = request.POST.get('birimAdi')
        kurum_adi = request.POST.get('kurumAdi')
        hsa_kodu_str = request.POST.get('hsaKodu')

        if not all([birim_adi, kurum_adi, hsa_kodu_str]):
             return JsonResponse({'status': 'error', 'message': 'Tüm alanlar zorunludur.'}, status=400)

        hsa_nesnesi = get_object_or_404(HizmetSunumAlani, AlanKodu=hsa_kodu_str)
        
        # Aynı isimde başka birim var mı kontrol et (opsiyonel)
        # if Birim.objects.filter(BirimAdi=birim_adi).exists():
        #    return JsonResponse({'status': 'error', 'message': 'Bu isimde bir birim zaten mevcut.'}, status=400)

        with transaction.atomic(): # Atomik işlem başlat
            birim = Birim.objects.create(
                BirimAdi=birim_adi,
                KurumAdi=kurum_adi,
                HSAKodu=hsa_nesnesi 
                # AlanKodu alanı modelde otomatik atanıyor olabilir, kontrol edin.
                # Eğer modelde AlanKodu'nu ayrıca set ediyorsanız, burada da yapın.
            )
            
            # Kullanıcıyı yeni birime otomatik olarak yetkilendir
            UserBirim.objects.create(user=request.user, birim=birim)
            
        return JsonResponse({'status': 'success', 'message': 'Birim başarıyla eklendi.'})
    except HizmetSunumAlani.DoesNotExist:
         return JsonResponse({'status': 'error', 'message': 'Geçersiz Hizmet Sunum Alanı kodu.'}, status=400)
    except Exception as e:
        # Hata loglama eklenebilir
        return JsonResponse({'status': 'error', 'message': f'Birim eklenirken hata oluştu: {str(e)}'}, status=500)
    
@login_required
@require_POST
def birim_guncelle(request, birim_id):
    # Kullanıcının bu birime yetkisi var mı kontrol et
    if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
        
    birim = get_object_or_404(Birim, BirimId=birim_id)
    
    try:
        birim_adi = request.POST.get('birimAdi')
        kurum_adi = request.POST.get('kurumAdi')
        hsa_kodu_str = request.POST.get('hsaKodu')

        if not all([birim_adi, kurum_adi, hsa_kodu_str]):
             return JsonResponse({'status': 'error', 'message': 'Tüm alanlar zorunludur.'}, status=400)

        hsa_nesnesi = get_object_or_404(HizmetSunumAlani, AlanKodu=hsa_kodu_str)

        # Aynı isimde başka birim var mı kontrol et (kendisi hariç)
        # if Birim.objects.filter(BirimAdi=birim_adi).exclude(BirimId=birim_id).exists():
        #    return JsonResponse({'status': 'error', 'message': 'Bu isimde başka bir birim zaten mevcut.'}, status=400)

        birim.BirimAdi = birim_adi
        birim.KurumAdi = kurum_adi
        birim.HSAKodu = hsa_nesnesi
        # AlanKodu alanı modelde otomatik atanıyor olabilir, kontrol edin.
        birim.save()
        return JsonResponse({'status': 'success', 'message': 'Birim başarıyla güncellendi.'})
    except HizmetSunumAlani.DoesNotExist:
         return JsonResponse({'status': 'error', 'message': 'Geçersiz Hizmet Sunum Alanı kodu.'}, status=400)
    except Exception as e:
        # Hata loglama eklenebilir
        return JsonResponse({'status': 'error', 'message': f'Birim güncellenirken hata oluştu: {str(e)}'}, status=500)

@login_required
@require_POST
def birim_sil(request, birim_id):
    # Kullanıcının bu birime yetkisi var mı kontrol et
    if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
        
    birim = get_object_or_404(Birim, BirimId=birim_id)
    
    try:
        with transaction.atomic():
            # İlişkili HizmetSunumCalismasi kayıtları varsa ne yapılacağına karar verin.
            # Modelde on_delete=models.CASCADE varsa, birim silinince çalışmalar da silinir.
            # Eğer silinmemesi gerekiyorsa veya başka bir işlem yapılacaksa burada ele alınmalı.
            # Örneğin:
            # if HizmetSunumCalismasi.objects.filter(CalisilanBirimId=birim).exists():
            #     return JsonResponse({'status': 'error', 'message': 'Bu birime ait çalışma kayıtları olduğu için silinemez.'}, status=400)
            
            birim_adi = birim.BirimAdi # Silmeden önce adı alalım
            birim.delete()
        return JsonResponse({'status': 'success', 'message': f'{birim_adi} birimi başarıyla silindi.'})
    except Exception as e:
         # Hata loglama eklenebilir
        return JsonResponse({'status': 'error', 'message': f'Birim silinirken hata oluştu: {str(e)}'}, status=500)

@login_required
@require_GET
def onceki_donem_personel(request, donem, birim_id):
    """Bir önceki döneme ait personelleri getir (Mevcut fonksiyon doğru görünüyor)"""
    # Yetki kontrolü eklenebilir
    if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
        
    try:
        donem_date = datetime.strptime(donem, '%Y-%m')
        if donem_date.month == 1:
            onceki_ay = datetime(donem_date.year - 1, 12, 1)
        else:
            onceki_ay = datetime(donem_date.year, donem_date.month - 1, 1)
            
        # Önceki dönem personellerini getir
        # Model alan adlarının doğru olduğunu varsayıyoruz (PersonelId__PersonelId vs.)
        personeller_qs = HizmetSunumCalismasi.objects.filter(
            CalisilanBirimId_id=birim_id,
            Donem=onceki_ay.date()
        ).select_related('PersonelId').values(
            'PersonelId__PersonelId', # Personel modelinin PK'sı
            'PersonelId__TCKimlikNo', # TC Kimlik No eklendi
            'PersonelId__PersonelAdi',
            'PersonelId__PersonelSoyadi'
        ).distinct()
        
        data = [{
            'personel_id': p['PersonelId__PersonelId'],
            'tc_kimlik': p['PersonelId__TCKimlikNo'], # TC Kimlik No eklendi
            'adi': p['PersonelId__PersonelAdi'],
            'soyadi': p['PersonelId__PersonelSoyadi']
        } for p in personeller_qs]
        
        # Başarı durumunda status eklemek iyi pratik olabilir
        return JsonResponse(data, safe=False) # Direkt listeyi döndür
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_POST
def personel_kaydet(request):
    """Personel kayıtlarını oluşturur. Aynı dönem/birim için mükerrer personel eklemeye izin verir."""
    try:
        data = json.loads(request.body)
        donem_str = data.get('donem')
        birim_id = data.get('birim_id')
        personeller_data = data.get('personeller', [])

        if not donem_str or not birim_id:
            return JsonResponse({'status': 'error', 'message': 'Dönem veya Birim ID eksik.'}, status=400)
        
        if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
            return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)

        donem = datetime.strptime(donem_str, '%Y-%m')
        baslangic = donem.replace(day=1).date()
        bitis = donem.replace(day=calendar.monthrange(donem.year, donem.month)[1]).date()
        
        birim = get_object_or_404(Birim.objects.select_related('HSAKodu'), BirimId=birim_id)
        alan_kodu = birim.HSAKodu.AlanKodu if birim.HSAKodu else None
        
        created_count = 0
        error_list = []

        with transaction.atomic():
            for p_data in personeller_data:
                tc_kimlik = p_data.get('tc_kimlik', '').strip()
                adi = p_data.get('adi', '').strip()
                soyadi = p_data.get('soyadi', '').strip()
                
                if not (tc_kimlik and adi and soyadi):
                    error_list.append(f"Eksik bilgi (TC: {tc_kimlik}, Ad: {adi}, Soyad: {soyadi})")
                    continue

                try:
                    # Personel'i al veya oluştur/güncelle
                    personel, p_created = Personel.objects.update_or_create(
                        TCKimlikNo=tc_kimlik,
                        defaults={'PersonelAdi': adi, 'PersonelSoyadi': soyadi}
                    )
                    
                    # Her zaman yeni HizmetSunumCalismasi kaydı oluştur
                    HizmetSunumCalismasi.objects.create(
                        PersonelId=personel,
                        CalisilanBirimId=birim,
                        Donem=baslangic,
                        HizmetBaslangicTarihi=baslangic,
                        HizmetBitisTarihi=bitis,
                        CreatedBy=request.user,
                        OzelAlanKodu=alan_kodu,
                        Sorumlu=False,
                        Sertifika=False,
                        Kesinlestirme=False
                    )
                    created_count += 1
                except Exception as inner_e:
                    error_list.append(f"TC: {tc_kimlik} için hata: {str(inner_e)}")

        message = f"{created_count} personel için bildirim kaydı oluşturuldu."
        if error_list:
             message += f" Hatalar: {'; '.join(error_list)}"
             status_code = 207 if created_count > 0 else 400
             return JsonResponse({'status': 'warning' if created_count > 0 else 'error', 'message': message}, status=status_code)

        return JsonResponse({'status': 'success', 'message': message})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON formatı.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Genel hata: {str(e)}'}, status=500)

@login_required
@require_GET
def bildirimler_listele(request, year, month, birim_id):
    """
    Seçili yıl, ay ve birim için bildirimleri JSON olarak döndürür.
    (Mevcut fonksiyon doğru görünüyor, yetki kontrolü eklenebilir)
    """
    # Yetki kontrolü
    if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
        
    try:
        donem = date(year, month, 1)
        # İlgili birim nesnesini de alalım (HSA adı için)
        birim = get_object_or_404(Birim.objects.select_related('HSAKodu'), BirimId=birim_id)
        hsa_adi = birim.HSAKodu.AlanAdi if birim.HSAKodu else "Tanımsız"

        bildirimler = HizmetSunumCalismasi.objects.filter(
            CalisilanBirimId_id=birim_id,
            Donem=donem
        ).select_related('PersonelId').order_by('PersonelId__PersonelSoyadi', 'PersonelId__PersonelAdi') # Sıralama ekleyelim

        data = []
        for b in bildirimler:
            # getattr kullanımı yerine doğrudan erişim daha okunaklı olabilir
            personel = b.PersonelId
            data.append({
                'id': b.CalismaId,
                'tc_kimlik_no': personel.TCKimlikNo if personel else '',
                'ad': personel.PersonelAdi if personel else '',
                'soyad': personel.PersonelSoyadi if personel else '',
                'baslangic': b.HizmetBaslangicTarihi.strftime('%Y-%m-%d') if b.HizmetBaslangicTarihi else '',
                'bitis': b.HizmetBitisTarihi.strftime('%Y-%m-%d') if b.HizmetBitisTarihi else '',
                'ozel_alan_kodu': b.OzelAlanKodu,
                'sorumlu': b.Sorumlu,
                'sertifika': b.Sertifika,
                'kesinlesmis': b.Kesinlestirme,
            })

        # Başarı durumunda seçili birim bilgilerini de gönderelim
        return JsonResponse({
            'status': 'success', 
            'data': data,
            'birim_adi': birim.BirimAdi,
            'hsa_adi': hsa_adi,
            'alan_kodu': birim.HSAKodu.AlanKodu if birim.HSAKodu else None
        })
    except Exception as e:
        # Hata loglama eklenebilir
        return JsonResponse({'status': 'error', 'message': f'Bildirimler listelenirken hata: {str(e)}'}, status=500)

@csrf_exempt
@login_required
def bildirimler_kaydet(request):
    """Bildirim tablosundaki değişiklikleri kaydeder"""
    try:
        data = json.loads(request.body)
        donem_str = data.get('donem')
        birim_id = data.get('birim_id')
        bildirimler_data = data.get('bildirimler', [])

        if not donem_str or not birim_id:
            return JsonResponse({'status': 'error', 'message': 'Dönem veya Birim ID eksik.'}, status=400)
        
        # Yetki kontrolü
        if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
            return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)

        donem_date = datetime.strptime(donem_str, '%Y-%m').date()
        donem_baslangic = donem_date.replace(day=1)
        donem_bitis = donem_date.replace(day=calendar.monthrange(donem_date.year, donem_date.month)[1])
        
        birim = get_object_or_404(Birim.objects.select_related('HSAKodu'), BirimId=birim_id)
        alan_kodu = birim.HSAKodu.AlanKodu if birim.HSAKodu else None
        
        errors = []
        bildirim_nesneleri = [] # Geçerli verileri tutmak için

        # 1. Adım: Gelen veriyi doğrula ve nesnelere dönüştür
        for index, b_data in enumerate(bildirimler_data):
            bildirim_id = b_data.get('id')
            # Bildirim ID'sinin integer olduğundan emin olalım veya None yapalım
            try:
                bildirim_id = int(bildirim_id) if bildirim_id else None
            except ValueError:
                 errors.append({'index': index, 'id': b_data.get('id'), 'message': 'Geçersiz Bildirim ID formatı.'})
                 continue # Bu satırla devam etme
                 
            tc_kimlik_no = b_data.get('tc_kimlik_no', '').strip()
            baslangic_str = b_data.get('baslangic')
            bitis_str = b_data.get('bitis')
            sorumlu = b_data.get('sorumlu', False)
            sertifika = b_data.get('sertifika', False)
            
            if not (tc_kimlik_no and baslangic_str and bitis_str):
                 errors.append({'index': index, 'tc_kimlik_no': tc_kimlik_no, 'id': bildirim_id, 'message': 'TC Kimlik No, Başlangıç ve Bitiş tarihleri zorunludur.'})
                 continue

            try:
                baslangic = datetime.strptime(baslangic_str, '%Y-%m-%d').date()
                bitis = datetime.strptime(bitis_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append({'index': index, 'tc_kimlik_no': tc_kimlik_no, 'id': bildirim_id, 'message': 'Geçersiz tarih formatı.'})
                continue

            if baslangic > bitis:
                errors.append({'index': index, 'tc_kimlik_no': tc_kimlik_no, 'id': bildirim_id, 'message': 'Başlangıç tarihi, bitiş tarihinden sonra olamaz.'})
                continue
            if baslangic < donem_baslangic or baslangic > donem_bitis:
                errors.append({'index': index, 'tc_kimlik_no': tc_kimlik_no, 'id': bildirim_id, 'message': f'Başlangıç tarihi ({baslangic_str}) seçili dönem ({donem_str}) dışında.'})
                continue
            if bitis < donem_baslangic or bitis > donem_bitis:
                 errors.append({'index': index, 'tc_kimlik_no': tc_kimlik_no, 'id': bildirim_id, 'message': f'Bitiş tarihi ({bitis_str}) seçili dönem ({donem_str}) dışında.'})
                 continue
                 
            bildirim_nesneleri.append({
                'index': index, 
                'id': bildirim_id,
                'tc_kimlik_no': tc_kimlik_no,
                'baslangic': baslangic,
                'bitis': bitis,
                'sorumlu': sorumlu,
                'sertifika': sertifika
            })

        # Eğer temel doğrulama hataları varsa, devam etme
        if errors:
             return JsonResponse({
                'status': 'error', 
                'message': 'Lütfen tablodaki hataları düzeltin.', 
                'errors': errors
            }, status=400)

        # 2. Adım: Çakışma Kontrolü ve Kayıt
        with transaction.atomic():
            processed_indices = set()
            final_errors = [] 

            # --- Çakışma Kontrolleri --- 
            for current_b in bildirim_nesneleri:
                if current_b['index'] in processed_indices: continue

                personel = Personel.objects.filter(TCKimlikNo=current_b['tc_kimlik_no']).first()
                if not personel:
                    final_errors.append({'index': current_b['index'], 'tc_kimlik_no': current_b['tc_kimlik_no'], 'id': current_b['id'], 'message': 'Personel bulunamadı.'})
                    processed_indices.add(current_b['index'])
                    continue

                # Kendi içinde çakışma
                has_internal_conflict = False
                for other_b in bildirim_nesneleri:
                    if current_b['index'] == other_b['index'] or other_b['index'] in processed_indices: continue
                    if current_b['tc_kimlik_no'] == other_b['tc_kimlik_no'] and max(current_b['baslangic'], other_b['baslangic']) <= min(current_b['bitis'], other_b['bitis']):
                        err_msg_current = f"Girilen listede çakışan tarih: {other_b['baslangic']} - {other_b['bitis']}"
                        err_msg_other = f"Girilen listede çakışan tarih: {current_b['baslangic']} - {current_b['bitis']}"
                        if current_b['index'] not in processed_indices:
                            final_errors.append({'index': current_b['index'], 'tc_kimlik_no': current_b['tc_kimlik_no'], 'id': current_b['id'], 'message': err_msg_current})
                            processed_indices.add(current_b['index'])
                            has_internal_conflict = True
                        if other_b['index'] not in processed_indices:
                            final_errors.append({'index': other_b['index'], 'tc_kimlik_no': other_b['tc_kimlik_no'], 'id': other_b['id'], 'message': err_msg_other})
                            processed_indices.add(other_b['index'])
                if has_internal_conflict: continue

                # Veritabanı ile çakışma
                cakisma_sorgusu = Q(
                    PersonelId=personel,
                    HizmetBaslangicTarihi__lte=current_b['bitis'],
                    HizmetBitisTarihi__gte=current_b['baslangic']
                )
                if current_b['id']:
                    cakisma_sorgusu &= ~Q(CalismaId=current_b['id'])
                cakisan_kayitlar = HizmetSunumCalismasi.objects.filter(cakisma_sorgusu)
                if cakisan_kayitlar.exists():
                    hata_mesaji = "Çakışan kayıtlar: \n".join ([f"{c.CalisilanBirimId.BirimAdi} Biriminde: {c.HizmetBaslangicTarihi.strftime('%d.%m')}-{c.HizmetBitisTarihi.strftime('%d.%m.%Y')}\n" for c in cakisan_kayitlar])
                    final_errors.append({'index': current_b['index'], 'tc_kimlik_no': current_b['tc_kimlik_no'], 'id': current_b['id'], 'message': hata_mesaji})
                    processed_indices.add(current_b['index'])
                    continue
            
            # Eğer çakışma veya hata varsa işlemi geri al ve bitir
            if final_errors:
                 transaction.set_rollback(True) 
                 return JsonResponse({
                    'status': 'error', 
                    'message': 'Çakışan veya hatalı kayıtlar bulundu. Kayıt işlemi geri alındı.', 
                    'errors': final_errors
                }, status=400)

            # --- Kayıt/Güncelleme --- 
            for b_data in bildirim_nesneleri: 
                 try:
                     personel = Personel.objects.get(TCKimlikNo=b_data['tc_kimlik_no']) # Get personel again inside loop
                     if b_data['id']: # ID varsa güncelle
                         calisma = HizmetSunumCalismasi.objects.get(CalismaId=b_data['id'], CalisilanBirimId=birim) 
                         calisma.HizmetBaslangicTarihi = b_data['baslangic']
                         calisma.HizmetBitisTarihi = b_data['bitis']
                         calisma.Sorumlu = b_data['sorumlu']
                         calisma.Sertifika = b_data['sertifika']
                         calisma.LastUpdatedBy = request.user
                         calisma.LastUpdateDate = timezone.now()
                         calisma.save()
                     else: # ID yoksa yeni oluştur
                          HizmetSunumCalismasi.objects.create(
                             PersonelId=personel,
                             CalisilanBirimId=birim,
                             Donem=donem_baslangic, 
                             HizmetBaslangicTarihi=b_data['baslangic'],
                             HizmetBitisTarihi=b_data['bitis'],
                             Sorumlu=b_data['sorumlu'],
                             Sertifika=b_data['sertifika'],
                             CreatedBy=request.user,
                             OzelAlanKodu=alan_kodu,
                             Kesinlestirme=False
                         )
                 except HizmetSunumCalismasi.DoesNotExist:
                      final_errors.append({'index': b_data['index'], 'id': b_data['id'], 'message': 'Güncellenmek istenen kayıt bulunamadı.'})
                      transaction.set_rollback(True) 
                      return JsonResponse({
                            'status': 'error', 
                            'message': 'Kayıt sırasında hata oluştu (kayıt bulunamadı).', 
                            'errors': final_errors
                        }, status=400)
                 except Exception as save_error:
                      final_errors.append({'index': b_data['index'], 'id': b_data['id'], 'message': f'Kayıt hatası: {str(save_error)}'})
                      transaction.set_rollback(True) 
                      return JsonResponse({
                            'status': 'error', 
                            'message': 'Kayıt sırasında beklenmedik bir hata oluştu.', 
                            'errors': final_errors
                        }, status=500)

        # Hata yoksa işlem başarılıdır
        return JsonResponse({'status': 'success', 'message': 'Değişiklikler başarıyla kaydedildi.'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON formatı.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Genel bir hata oluştu: {str(e)}'}, status=500)

@csrf_exempt
@login_required
def bildirimler_kesinlestir(request):
    """Bildirimleri kesinleştirir"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            donem = data.get('donem')
            birim_id = data.get('birim_id')
            bildirimler_data = data.get('bildirimler')

            if not all([donem, birim_id, bildirimler_data]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Eksik parametreler.'
                })

            # Önce bildirimleri kaydet
            kaydet_sonucu = bildirimler_kaydet(request)
            if kaydet_sonucu.status_code != 200 or json.loads(kaydet_sonucu.content)['status'] == 'error':
                # Kaydetme başarısız olursa işlemi durdur
                return kaydet_sonucu

            donem_date = datetime.strptime(donem, '%Y-%m').date()
            birim = get_object_or_404(Birim, BirimId=birim_id)

            with transaction.atomic():
                for bildirim_data in bildirimler_data:
                    bildirim_id = bildirim_data.get('id')
                    if not bildirim_id:
                        continue

                    bildirim = get_object_or_404(HizmetSunumCalismasi, CalismaId=bildirim_id)
                    
                    # Verileri güncelle
                    bildirim.HizmetBaslangicTarihi = datetime.strptime(bildirim_data['baslangic'], '%Y-%m-%d').date()
                    bildirim.HizmetBitisTarihi = datetime.strptime(bildirim_data['bitis'], '%Y-%m-%d').date()
                    bildirim.Sorumlu = bildirim_data['sorumlu']
                    bildirim.Sertifika = bildirim_data['sertifika']
                    bildirim.Kesinlestirme = True
                    bildirim.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Bildirimler başarıyla kesinleştirildi.'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Geçersiz istek metodu.'
    })

@login_required
@require_POST
def bildirim_sil(request, bildirim_id):
    """Bildirim kaydını siler"""
    try:
        # ID integer değilse hata verecektir, kontrol edelim
        try:
            bildirim_id_int = int(bildirim_id)
        except ValueError:
             return JsonResponse({'status': 'error', 'message': 'Geçersiz Bildirim ID.'}, status=400)
             
        bildirim = get_object_or_404(HizmetSunumCalismasi, CalismaId=bildirim_id_int)
        
        # Kullanıcının bu bildirimin ait olduğu birime yetkisi var mı?
        if not UserBirim.objects.filter(user=request.user, birim=bildirim.CalisilanBirimId).exists():
             return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
             
        # Kesinleşmiş kayıt silinemez kontrolü
        if bildirim.Kesinlestirme:
            return JsonResponse({'status': 'error', 'message': 'Kesinleşmiş kayıtlar silinemez.'}, status=400)

        bildirim.delete()
        return JsonResponse({'status': 'success', 'message': 'Bildirim başarıyla silindi.'})
        
    except HizmetSunumCalismasi.DoesNotExist:
         return JsonResponse({'status': 'error', 'message': 'Bildirim bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Bildirim silinirken hata oluştu: {str(e)}'}, status=500)
