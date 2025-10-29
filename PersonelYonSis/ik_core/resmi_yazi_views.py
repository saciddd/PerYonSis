from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string, get_template
import pdfkit
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages # Import messages framework
from django.contrib.auth.decorators import login_required
from .models.personel import Personel
from django.db import models
from .models.Teblig import TebligImzasi
from .models.ResmiYazi import ResmiYazi
from .forms import ResmiYaziForm

@login_required
def resmi_yazi_olustur(request, personel_id):
    personel = get_object_or_404(Personel, id=personel_id)
    imzalar = TebligImzasi.objects.all()
    resmi_yazilar = ResmiYazi.objects.all()
    return render(request, 'ik_core/resmi_yazi.html', {
        'personel': personel,
        'imzalar': imzalar,
        'resmi_yazilar': resmi_yazilar,
    })

@login_required
def resmi_yazi_tanimlari(request):
    resmi_yazilar = ResmiYazi.objects.all()
    return render(request, 'ik_core/resmi_yazi_tanimlari.html', {
        'resmi_yazilar': resmi_yazilar,
    })

@login_required
@require_POST
def resmi_yazi_ekle(request):
    ad = request.POST.get('ad')
    metin = request.POST.get('metin')
    ilgi = request.POST.get('ilgi', '')
    ek = request.POST.get('ek', '')
    if ad and metin:
        ResmiYazi.objects.create(ad=ad, metin=metin, ilgi=ilgi, ek=ek)
        messages.success(request, 'Resmi yazı şablonu başarıyla eklendi.')
    else:
        messages.error(request, 'Ad ve metin alanları zorunludur.')
    return redirect('ik_core:resmi_yazi_tanimlari')

@login_required
@require_POST
def resmi_yazi_guncelle(request, yazi_id):
    sablon = get_object_or_404(ResmiYazi, id=yazi_id)
    ad = request.POST.get('ad')
    metin = request.POST.get('metin')
    ilgi = request.POST.get('ilgi', '')
    ek = request.POST.get('ek', '')
    if ad and metin:
        sablon.ad = ad
        sablon.metin = metin
        sablon.ilgi = ilgi
        sablon.ek = ek
        sablon.save()
        messages.success(request, 'Resmi yazı şablonu başarıyla güncellendi.')
    else:
        messages.error(request, 'Ad ve metin alanları zorunludur.')
    return redirect('ik_core:resmi_yazi_tanimlari')

@login_required
@require_POST
def resmi_yazi_sil(request, yazi_id):
    sablon = get_object_or_404(ResmiYazi, id=yazi_id)
    sablon.delete()
    messages.success(request, 'Resmi yazı şablonu başarıyla silindi.')
    return redirect('ik_core:resmi_yazi_tanimlari')

@login_required
def resmi_yazi_get(request, pk):
    sablon = get_object_or_404(ResmiYazi, id=pk)
    data = {
        'id': sablon.id,
        'ad': sablon.ad,
        'metin': sablon.metin,
        'ilgi': sablon.ilgi,
        'ek': sablon.ek,
    }
    return JsonResponse(data)