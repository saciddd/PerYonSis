from datetime import datetime, date
import calendar
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import HizmetSunumCalismasi, UserBirim, Birim, Personel
import json

@require_POST
def bildirim_kesinlestir(request):
    """
    Tekil bildirim kaydı için kesinleştirme işlemi.
    POST: { "bildirim_id": ... }
    """
    import json
    try:
        data = json.loads(request.body)
        bildirim_id = data.get("bildirim_id")
        if not bildirim_id:
            return JsonResponse({"status": "error", "message": "Bildirim ID gerekli."}, status=400)
        bildirim = get_object_or_404(HizmetSunumCalismasi, CalismaId=bildirim_id)
        if getattr(bildirim, "Kesinlestirme", False):
            return JsonResponse({"status": "error", "message": "Kayıt zaten kesinleşmiş."}, status=400)
        bildirim.Kesinlestirme = True
        bildirim.save(update_fields=["Kesinlestirme"])
        return JsonResponse({"status": "success", "message": "Kayıt kesinleştirildi."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@require_POST
def bildirim_kesinlestirmeyi_kaldir(request):
    """
    Tekil bildirim kaydı için kesinleştirmeyi kaldırma işlemi.
    POST: { "bildirim_id": ... }
    """
    try:
        data = json.loads(request.body)
        bildirim_id = data.get("bildirim_id")
        if not bildirim_id:
            return JsonResponse({"status": "error", "message": "Bildirim ID gerekli."}, status=400)
        bildirim = get_object_or_404(HizmetSunumCalismasi, CalismaId=bildirim_id)
        if not getattr(bildirim, "Kesinlestirme", False):
            return JsonResponse({"status": "error", "message": "Kayıt zaten beklemede."}, status=400)
        bildirim.Kesinlestirme = False
        bildirim.save(update_fields=["Kesinlestirme"])
        return JsonResponse({"status": "success", "message": "Kesinleştirme kaldırıldı."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
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
        if not request.user.has_permission('HSA Bildirim Kesinleştirme'):
            if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
                return JsonResponse({'status': 'error', 'message': 'Yetkisiz erişim'}, status=403)
        # Yetkisi varsa veya UserBirim ilişkisi varsa devam et


        donem_date = datetime.strptime(donem_str, '%Y-%m').date()
        donem_baslangic = donem_date.replace(day=1)
        donem_bitis = donem_date.replace(day=calendar.monthrange(donem_date.year, donem_date.month)[1])
        
        birim = get_object_or_404(Birim.objects.select_related('HSAKodu'), BirimId=birim_id)
        alan_kodu = birim.HSAKodu.AlanKodu if birim.HSAKodu else None
        
        errors = []
        bildirim_nesneleri = []

        # 1. Adım: Gelen veriyi doğrula ve nesnelere dönüştür
        for index, b_data in enumerate(bildirimler_data):
            bildirim_id = b_data.get('id')
            try:
                bildirim_id = int(bildirim_id) if bildirim_id else None
            except ValueError:
                errors.append({'index': index, 'id': b_data.get('id'), 'message': 'Geçersiz Bildirim ID formatı.'})
                continue
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

        processed_indices = set()
        final_errors = []
        kaydedilenler = 0

        for current_b in bildirim_nesneleri:
            if current_b['index'] in processed_indices:
                continue
            personel = Personel.objects.filter(TCKimlikNo=current_b['tc_kimlik_no']).first()
            if not personel:
                final_errors.append({
                    'index': current_b['index'],
                    'id': current_b['id'],
                    'message': 'Personel bulunamadı.'
                })
                processed_indices.add(current_b['index'])
                continue

            # Kayıt/Güncelleme
            try:
                if current_b['id']:
                    calisma = HizmetSunumCalismasi.objects.get(CalismaId=current_b['id'], CalisilanBirimId=birim)
                    calisma.HizmetBaslangicTarihi = current_b['baslangic']
                    calisma.HizmetBitisTarihi = current_b['bitis']
                    calisma.Sorumlu = current_b['sorumlu']
                    calisma.Sertifika = current_b['sertifika']
                    calisma.LastUpdatedBy = request.user
                    calisma.LastUpdateDate = timezone.now()
                    calisma.save()
                else:
                    HizmetSunumCalismasi.objects.create(
                        PersonelId=personel,
                        CalisilanBirimId=birim,
                        Donem=donem_baslangic, 
                        HizmetBaslangicTarihi=current_b['baslangic'],
                        HizmetBitisTarihi=current_b['bitis'],
                        Sorumlu=current_b['sorumlu'],
                        Sertifika=current_b['sertifika'],
                        CreatedBy=request.user,
                        OzelAlanKodu=alan_kodu,
                        Kesinlestirme=False
                    )
                kaydedilenler += 1
            except Exception as save_error:
                final_errors.append({
                    'index': current_b['index'],
                    'id': current_b['id'],
                    'message': f'Kayıt hatası: {str(save_error)}'
                })
                processed_indices.add(current_b['index'])
                continue

            # Kayıt/güncelleme sonrası veritabanı çakışma kontrolü
            cakisma_sorgusu = Q(
                PersonelId=personel,
                HizmetBaslangicTarihi__lte=current_b['bitis'],
                HizmetBitisTarihi__gte=current_b['baslangic']
            )
            if current_b['id']:
                cakisma_sorgusu &= ~Q(CalismaId=current_b['id'])
            cakisan_kayitlar = HizmetSunumCalismasi.objects.filter(cakisma_sorgusu)
            if cakisan_kayitlar.exists():
                hata_mesaji = "Çakışan kayıtlar: \n" + "; ".join([
                    f"{c.PersonelId.PersonelAdi} {c.PersonelId.PersonelSoyadi} - {c.CalisilanBirimId.BirimAdi} Biriminde: {c.HizmetBaslangicTarihi.strftime('%d.%m')}-{c.HizmetBitisTarihi.strftime('%d.%m.%Y')}"
                    for c in cakisan_kayitlar
                ])
                final_errors.append({
                    'index': current_b['index'],
                    'id': current_b['id'],
                    'message': hata_mesaji
                })

        # Hata mesajı oluştur
        all_errors = errors + final_errors
        if all_errors:
            msg = f"{kaydedilenler} kayıt kaydedildi. {len(all_errors)} kayıt kaydedilemedi veya çakıştı."
            return JsonResponse({
                'status': 'partial' if kaydedilenler > 0 else 'error',
                'message': msg,
                'errors': all_errors
            }, status=207 if kaydedilenler > 0 else 400)
        return JsonResponse({'status': 'success', 'message': f'Tüm kayıtlar başarıyla kaydedildi.'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON formatı.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Genel bir hata oluştu: {str(e)}'}, status=500)