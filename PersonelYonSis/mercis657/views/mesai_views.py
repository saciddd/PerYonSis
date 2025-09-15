from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Mesai_Tanimlari
from ..forms import MesaiTanimForm
from datetime import timedelta
from .main_views import tanimlamalar

# Yeni Mesai Tanımı Ekleme Fonksiyonu
def add_mesai_tanim(request):
    if request.method == 'POST':
        form = MesaiTanimForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            # Renk siyah veya boş ise None kaydet
            renk = form.cleaned_data.get('Renk')
            if not renk or renk.lower() == '#000000':
                obj.Renk = None
            obj.calculate_sure()
            obj.save()
            messages.success(request, "Mesai kaydı eklendi")
            return redirect('mercis657:tanimlamalar')
        # Geçersiz ise aynı sayfayı form hatalarıyla render et
        tanimlamalar(request)
    return redirect('mercis657:tanimlamalar')

def mesai_tanim_update(request):
    mesai_id = request.POST.get('mesai_id')
    mesai = get_object_or_404(Mesai_Tanimlari, id=mesai_id)
    if request.method == 'POST':
        form = MesaiTanimForm(request.POST, instance=mesai)
        if form.is_valid():
            obj = form.save(commit=False)
            renk = form.cleaned_data.get('Renk')
            if not renk or renk.lower() == '#000000':
                obj.Renk = None
            obj.calculate_sure()
            obj.save()
            return JsonResponse({'status': 'success'})
        # Form hatalarını döndür
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'}, status=405)

@login_required
def mesai_tanim_form(request, pk):
    """Modal için form HTML döndürür (edit)."""
    mesai = get_object_or_404(Mesai_Tanimlari, pk=pk)
    form = MesaiTanimForm(instance=mesai)
    return render(request, 'mercis657/_mesai_tanim_form.html', {
        'form': form,
        'mesai': mesai,
    })
def delete_mesai_tanim(request):
    if request.method == 'POST':
        mesai_id = request.POST.get('mesai_id')
        try:
            mesai = get_object_or_404(Mesai_Tanimlari, id=mesai_id)
            mesai.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})
