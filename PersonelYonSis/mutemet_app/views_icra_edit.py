from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import IcraTakibi, Personel
from datetime import datetime
from django.http import JsonResponse

@login_required
@csrf_exempt
def icra_takibi_duzenle_modal(request, icra_id):
    """İcra düzenleme modalı için formu döndürür (AJAX)."""
    icra = get_object_or_404(IcraTakibi, pk=icra_id)
    return render(request, 'mutemet_app/_icra_duzenle_modal_content.html', {'icra': icra})

@login_required
@csrf_exempt
def icra_takibi_guncelle(request, icra_id):
    """İcra kaydını günceller (POST)."""
    icra = get_object_or_404(IcraTakibi, pk=icra_id)
    if request.method == 'POST':
        try:
            icra.icra_vergi_dairesi_no = request.POST.get('icra_vergi_dairesi_no', '')
            icra.icra_dairesi = request.POST.get('icra_dairesi', '')
            icra.dosya_no = request.POST.get('dosya_no', '')
            icra.icra_dairesi_banka = request.POST.get('icra_dairesi_banka', '')
            icra.icra_dairesi_hesap_no = request.POST.get('icra_dairesi_hesap_no', '')
            icra.alacakli = request.POST.get('alacakli', '')
            icra.alacakli_vekili = request.POST.get('alacakli_vekili', '')
            icra.icra_turu = request.POST.get('icra_turu', 'ICRA')
            tutar = request.POST.get('tutar', '0')
            try:
                icra.tutar = float(tutar)
            except Exception:
                messages.error(request, 'Tutar sayısal olmalı.')
                return JsonResponse({'success': False, 'message': 'Tutar sayısal olmalı.'})
            tarihi = request.POST.get('tarihi', '')
            try:
                icra.tarihi = datetime.strptime(tarihi, '%Y-%m-%d').date()
            except Exception:
                messages.error(request, 'Tarih formatı hatalı.')
                return JsonResponse({'success': False, 'message': 'Tarih formatı hatalı.'})
            icra.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})
