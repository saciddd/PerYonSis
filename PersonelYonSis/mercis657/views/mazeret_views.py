import calendar
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from datetime import datetime
import json
from ..models import Personel, PersonelListesi, PersonelListesiKayit, MazeretKaydi, Mesai, Mesai_Tanimlari, ResmiTatil
from ..utils import hesapla_fazla_mesai

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

