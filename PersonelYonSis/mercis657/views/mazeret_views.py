from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import json
from ..models import Personel, PersonelListesi, PersonelListesiKayit, MazeretKaydi, Mesai, Mesai_Tanimlari
from ..utils import hesapla_fazla_mesai


@login_required
def personel_profil(request, personel_id, liste_id, year, month):
    """Personel profil modalını döner"""
    personel = get_object_or_404(Personel, pk=personel_id)
    liste = get_object_or_404(PersonelListesi, pk=liste_id)
    
    # PersonelListesiKayit'ı al veya oluştur
    kayit, created = PersonelListesiKayit.objects.get_or_create(
        liste=liste,
        personel=personel,
        defaults={'radyasyon_calisani': False}
    )
    
    # Mazeret kayıtları
    mazeret_kayitlari = MazeretKaydi.objects.filter(personel=personel).order_by('-baslangic_tarihi')
    
    # Fazla mesai hesapla
    hesaplama = hesapla_fazla_mesai(kayit, year, month)
    
    # Mesai tanımları (hazır şablon için)
    mesai_tanimlari = Mesai_Tanimlari.objects.filter(GecerliMesai=True)
    
    # O ayki mesai günleri (hazır şablon için)
    from datetime import date
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    mesai_gunleri = []
    
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        weekday = current_date.weekday()
        
        # Hafta içi ve resmi tatil değilse
        if weekday < 5:
            from ..models import ResmiTatil
            is_resmi_tatil = ResmiTatil.objects.filter(
                TatilTarihi=current_date
            ).exists()
            
            if not is_resmi_tatil:
                # Bu güne mesai girilmiş mi kontrol et
                mesai_var = Mesai.objects.filter(
                    Personel=personel,
                    MesaiDate=current_date,
                    OnayDurumu=True
                ).exists()
                
                mesai_gunleri.append({
                    'tarih': current_date,
                    'gun_adi': current_date.strftime('%A'),
                    'gun_no': day,
                    'mesai_var': mesai_var
                })
    
    return render(request, 'mercis657/personel_profil.html', {
        'personel': personel,
        'liste': liste,
        'kayit': kayit,
        'mazeret_kayitlari': mazeret_kayitlari,
        'hesaplama': hesaplama,
        'mesai_tanimlari': mesai_tanimlari,
        'mesai_gunleri': mesai_gunleri,
        'year': year,
        'month': month
    })


@login_required
@require_POST
def mazeret_ekle(request):
    """Yeni mazeret kaydı ekler"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        personel_id = data.get('personel_id')
        baslangic_tarihi = data.get('baslangic_tarihi')
        bitis_tarihi = data.get('bitis_tarihi')
        gunluk_azaltim_saat = data.get('gunluk_azaltim_saat')
        aciklama = data.get('aciklama', '')
        
        if not all([personel_id, baslangic_tarihi, bitis_tarihi, gunluk_azaltim_saat]):
            return JsonResponse({'status': 'error', 'message': 'Tüm alanlar doldurulmalı.'})
        
        personel = get_object_or_404(Personel, pk=personel_id)
        
        mazeret = MazeretKaydi.objects.create(
            personel=personel,
            baslangic_tarihi=baslangic_tarihi,
            bitis_tarihi=bitis_tarihi,
            gunluk_azaltim_saat=gunluk_azaltim_saat,
            aciklama=aciklama,
            created_by=request.user
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Mazeret kaydı eklendi.',
            'mazeret_id': mazeret.id
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def mazeret_guncelle(request, mazeret_id):
    """Mazeret kaydını günceller"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        mazeret = get_object_or_404(MazeretKaydi, pk=mazeret_id)
        data = json.loads(request.body)
        
        mazeret.baslangic_tarihi = data.get('baslangic_tarihi', mazeret.baslangic_tarihi)
        mazeret.bitis_tarihi = data.get('bitis_tarihi', mazeret.bitis_tarihi)
        mazeret.gunluk_azaltim_saat = data.get('gunluk_azaltim_saat', mazeret.gunluk_azaltim_saat)
        mazeret.aciklama = data.get('aciklama', mazeret.aciklama)
        mazeret.save()
        
        return JsonResponse({'status': 'success', 'message': 'Mazeret kaydı güncellendi.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def mazeret_sil(request, mazeret_id):
    """Mazeret kaydını siler"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        mazeret = get_object_or_404(MazeretKaydi, pk=mazeret_id)
        mazeret.delete()
        
        return JsonResponse({'status': 'success', 'message': 'Mazeret kaydı silindi.'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def radyasyon_toggle(request, personel_id, liste_id):
    """Personelin radyasyon çalışanı durumunu değiştirir"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        kayit = get_object_or_404(PersonelListesiKayit, personel_id=personel_id, liste_id=liste_id)
        kayit.radyasyon_calisani = not kayit.radyasyon_calisani
        kayit.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Radyasyon çalışanı durumu güncellendi.',
            'radyasyon_calisani': kayit.radyasyon_calisani
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def hazir_mesai_ata(request, personel_id, liste_id, year, month):
    """Seçilen günlere hazır mesai atar"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        mesai_tanim_id = data.get('mesai_tanim_id')
        gunler = data.get('gunler', [])  # [1, 5, 10] gibi gün numaraları
        
        if not mesai_tanim_id or not gunler:
            return JsonResponse({'status': 'error', 'message': 'Mesai tanımı ve günler seçilmelidir.'})
        
        personel = get_object_or_404(Personel, pk=personel_id)
        mesai_tanim = get_object_or_404(Mesai_Tanimlari, pk=mesai_tanim_id)
        
        from datetime import date
        created_count = 0
        
        for gun_no in gunler:
            current_date = date(year, month, gun_no)
            
            # Bu güne zaten mesai var mı kontrol et
            existing = Mesai.objects.filter(
                Personel=personel,
                MesaiDate=current_date
            ).first()
            
            if not existing:
                Mesai.objects.create(
                    Personel=personel,
                    MesaiDate=current_date,
                    MesaiTanim=mesai_tanim,
                    OnayDurumu=True,
                    Degisiklik=False
                )
                created_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} güne mesai atandı.',
            'created_count': created_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def toplu_islem(request, liste_id, year, month):
    """Toplu işlemler modalını döner"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    liste = get_object_or_404(PersonelListesi, pk=liste_id)
    personeller = Personel.objects.filter(personellistesikayit__liste=liste).distinct()
    mesai_tanimlari = Mesai_Tanimlari.objects.filter(GecerliMesai=True)
    
    return render(request, 'mercis657/toplu_islem_modal.html', {
        'liste': liste,
        'personeller': personeller,
        'mesai_tanimlari': mesai_tanimlari,
        'year': year,
        'month': month
    })


@login_required
@require_POST
def toplu_radyasyon_ata(request, liste_id):
    """Tüm personele radyasyon çalışanı durumu atar"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        radyasyon_calisani = data.get('radyasyon_calisani', False)
        
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        updated_count = PersonelListesiKayit.objects.filter(
            liste=liste
        ).update(radyasyon_calisani=radyasyon_calisani)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{updated_count} personelin radyasyon durumu güncellendi.',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def toplu_mesai_ata(request, liste_id, year, month):
    """Tüm personele toplu mesai atar"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        mesai_tanim_id = data.get('mesai_tanim_id')
        gunler = data.get('gunler', [])
        
        if not mesai_tanim_id or not gunler:
            return JsonResponse({'status': 'error', 'message': 'Mesai tanımı ve günler seçilmelidir.'})
        
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        mesai_tanim = get_object_or_404(Mesai_Tanimlari, pk=mesai_tanim_id)
        
        from datetime import date
        created_count = 0
        
        for personel in liste.kayitlar.all():
            for gun_no in gunler:
                current_date = date(year, month, gun_no)
                
                # Bu güne zaten mesai var mı kontrol et
                existing = Mesai.objects.filter(
                    Personel=personel.personel,
                    MesaiDate=current_date
                ).exists()
                
                if not existing:
                    Mesai.objects.create(
                        Personel=personel.personel,
                        MesaiDate=current_date,
                        MesaiTanim=mesai_tanim,
                        OnayDurumu=True,
                        Degisiklik=False
                    )
                    created_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} mesai kaydı oluşturuldu.',
            'created_count': created_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
