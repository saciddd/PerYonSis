from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Izin
import json
from django.contrib import messages

@require_POST
def izin_ekle(request):
    # Basit yetki kontrolü; gerekiyorsa değiştirin
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz'}, status=403)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        ad = payload.get('ad', '').strip()
        kod_raw = payload.get('kod', None)
        # normalize kod: boş -> None, sayısal -> int, değilse string
        kod = None
        if kod_raw is not None:
            kod_s = str(kod_raw).strip()
            if kod_s != '':
                try:
                    kod = int(kod_s)
                except ValueError:
                    kod = kod_s

        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Ad boş olamaz.'})
        # benzersizlik kontrolleri
        if Izin.objects.filter(ad__iexact=ad).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad ile izin zaten mevcut.'})

        izin = Izin.objects.create(ad=ad, kod=kod)
        messages.success(request, f"{ad} izni başarıyla eklendi.")
        return JsonResponse({'status': 'success', 'id': izin.id, 'kod': izin.kod})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@require_POST
def izin_guncelle(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Yetkisiz'}, status=403)
    izin = get_object_or_404(Izin, pk=pk)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        ad = payload.get('ad', '').strip()
        kod_raw = payload.get('kod', None)
        kod = None
        if kod_raw is not None:
            kod_s = str(kod_raw).strip()
            if kod_s != '':
                try:
                    kod = int(kod_s)
                except ValueError:
                    kod = kod_s

        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Ad boş olamaz.'})
        # çakışma kontrolleri (kendisi hariç)
        if Izin.objects.filter(ad__iexact=ad).exclude(pk=izin.pk).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad başka bir kayıtta kullanılıyor.'})

        izin.ad = ad
        izin.kod = kod
        izin.save()
        return JsonResponse({'status': 'success', 'id': izin.id, 'kod': izin.kod})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})