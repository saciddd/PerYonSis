from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models.personel import Personel
from .models.Teblig import TebligImzasi
from .models.DurumBelgesi import DurumBelgesi
from .forms import DurumBelgesiForm


@login_required
def durum_belgesi_olustur(request, personel_id):
    personel = get_object_or_404(Personel, id=personel_id)
    imzalar = TebligImzasi.objects.all()
    durum_belgeleri = DurumBelgesi.objects.all()
    return render(request, 'ik_core/durum_belgesi.html', {
        'personel': personel,
        'imzalar': imzalar,
        'durum_belgeleri': durum_belgeleri,
    })


@login_required
def durum_belgesi_tanimlari(request):
    durum_belgeleri = DurumBelgesi.objects.all()
    return render(request, 'ik_core/durum_belgesi_tanimlari.html', {
        'durum_belgeleri': durum_belgeleri,
    })


@login_required
@require_POST
def durum_belgesi_ekle(request):
    ad = request.POST.get('ad')
    metin = request.POST.get('metin')
    if ad and metin:
        DurumBelgesi.objects.create(ad=ad, metin=metin)
        messages.success(request, 'Durum belgesi şablonu başarıyla eklendi.')
    else:
        messages.error(request, 'Ad ve metin alanları zorunludur.')
    return redirect('ik_core:durum_belgesi_tanimlari')


@login_required
@require_POST
def durum_belgesi_guncelle(request, belge_id):
    sablon = get_object_or_404(DurumBelgesi, id=belge_id)
    ad = request.POST.get('ad')
    metin = request.POST.get('metin')
    if ad and metin:
        sablon.ad = ad
        sablon.metin = metin
        sablon.save()
        messages.success(request, 'Durum belgesi şablonu başarıyla güncellendi.')
    else:
        messages.error(request, 'Ad ve metin alanları zorunludur.')
    return redirect('ik_core:durum_belgesi_tanimlari')


@login_required
@require_POST
def durum_belgesi_sil(request, belge_id):
    sablon = get_object_or_404(DurumBelgesi, id=belge_id)
    sablon.delete()
    messages.success(request, 'Durum belgesi şablonu başarıyla silindi.')
    return redirect('ik_core:durum_belgesi_tanimlari')


@login_required
def durum_belgesi_get(request, pk):
    sablon = get_object_or_404(DurumBelgesi, id=pk)
    data = {
        'id': sablon.id,
        'ad': sablon.ad,
        'metin': sablon.metin,
    }
    return JsonResponse(data)

