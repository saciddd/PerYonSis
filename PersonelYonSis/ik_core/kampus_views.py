from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models.BirimYonetimi import Kampus, Bina
from .forms import KampusForm
import json

@login_required
def kampus_koordinat_editor(request):
    """
    Kampüs görseli üzerinde bina koordinatlarını belirlemek için kullanılan editör arayüzü.
    """
    kampusler = Kampus.objects.all()
    selected_kampus_id = request.GET.get('kampus_id')
    aktif_kampus = None
    binalar = []

    if selected_kampus_id:
        aktif_kampus = get_object_or_404(Kampus, id=selected_kampus_id)
        binalar = Bina.objects.filter(kampus=aktif_kampus).order_by('ad')
    elif kampusler.exists():
        # Varsayılan olarak ilk kampüsü seç
        aktif_kampus = kampusler.first()
        binalar = Bina.objects.filter(kampus=aktif_kampus).order_by('ad')

    context = {
        'kampusler': kampusler,
        'aktif_kampus': aktif_kampus,
        'binalar': binalar,
    }
    return render(request, 'ik_core/yonetim/kampus_koordinat_editor.html', context)

@login_required
@require_POST
def bina_koordinat_kaydet(request):
    """
    AJAX ile gönderilen bina koordinatlarını kaydeder.
    """
    try:
        data = json.loads(request.body)
        bina_id = data.get('bina_id')
        koordinatlar = data.get('koordinatlar')

        if not bina_id:
            return JsonResponse({'success': False, 'error': 'Bina ID eksik.'}, status=400)

        bina = get_object_or_404(Bina, id=bina_id)
        bina.koordinatlar = koordinatlar
        bina.save()

        return JsonResponse({'success': True, 'message': 'Koordinatlar başarıyla kaydedildi.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def kampus_tanimlari(request):
    """
    Kampus listeleme ve ekleme sayfası
    """
    if request.method == 'POST':
        form = KampusForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kampüs başarıyla eklendi.')
            return redirect('ik_core:kampus_tanimlari')
        else:
             messages.error(request, 'Kampüs eklenirken bir hata oluştu.')
    else:
        form = KampusForm()
        
    kampusler = Kampus.objects.all().order_by('ad')
    
    context = {
        'kampusler': kampusler,
        'form': form
    }
    return render(request, 'ik_core/yonetim/kampus_tanimlari.html', context)

@login_required
def kampus_duzenle(request, pk):
    """
    Kampus düzenleme
    """
    kampus = get_object_or_404(Kampus, pk=pk)
    if request.method == 'POST':
        form = KampusForm(request.POST, request.FILES, instance=kampus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kampüs başarıyla güncellendi.')
            return redirect('ik_core:kampus_tanimlari')
    else:
        form = KampusForm(instance=kampus)
        
    # Modal içinde kullanılacağı için tam sayfa render etmek yerine context ile bir şeyler yapılabilir
    # Ancak burada basitlik adına ayrı sayfa veya modal içeriği döndürebiliriz.
    # Şimdilik redirect ediyoruz çünkü modal form kullanacağız (muhtemelen).
    # Eğer modal kullanacaksak view farklı olmalı, ama standart yapıya uyalım.
    # Kullanıcı düzenleme için ayrı sayfaya gitmeyecek, modal içeriği alacak.
    
    # Basitlik için: Eğer AJAX ise modal content dön, değilse redirect.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
         return render(request, 'ik_core/partials/kampus_duzenle_form.html', {'form': form, 'kampus': kampus})
         
    return redirect('ik_core:kampus_tanimlari')

@login_required
def kampus_sil(request, pk):
    """
    Kampus silme
    """
    kampus = get_object_or_404(Kampus, pk=pk)
    if request.method == 'POST':
        kampus.delete()
        messages.success(request, 'Kampüs başarıyla silindi.')
    return redirect('ik_core:kampus_tanimlari')
