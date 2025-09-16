from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Bildirim, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin
from ..forms import ResmiTatilForm
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction

@login_required
@require_POST
def tatil_ekle(request):
    """ Yeni resmi tatil ekler """
    form = ResmiTatilForm(request.POST)
    
    if form.is_valid():
        # Aynı tarihe ait tatil kontrolü
        if ResmiTatil.objects.filter(TatilTarihi=form.cleaned_data['TatilTarihi']).exists():
            messages.error(request, "Bu tarihe ait bir resmi tatil zaten mevcut.")
            return redirect('mercis657:tanimlamalar')
        
        form.save()
        messages.success(request, "Resmi tatil başarıyla eklendi.")
    else:
        # Form hatalarını göster
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{form.fields[field].label}: {error}")
    
    return redirect('mercis657:tanimlamalar')

@login_required
@require_POST
def tatil_duzenle(request):
    """ Mevcut resmi tatili düzenler """
    tatil_id = request.POST.get('tatil_id')
    tatil = get_object_or_404(ResmiTatil, TatilID=tatil_id)
    
    form = ResmiTatilForm(request.POST, instance=tatil)
    
    if form.is_valid():
        # Aynı tarihe ait başka tatil kontrolü
        if ResmiTatil.objects.filter(TatilTarihi=form.cleaned_data['TatilTarihi']).exclude(TatilID=tatil_id).exists():
            messages.error(request, "Bu tarihe ait başka bir resmi tatil zaten mevcut.")
            return redirect('mercis657:tanimlamalar')
        
        form.save()
        messages.success(request, "Resmi tatil başarıyla güncellendi.")
    else:
        # Form hatalarını göster
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{form.fields[field].label}: {error}")
    
    return redirect('mercis657:tanimlamalar')

@login_required
@require_POST
def tatil_sil(request, tatil_id):
    """ Resmi tatili siler """
    tatil = get_object_or_404(ResmiTatil, TatilID=tatil_id)
    tatil.delete()
    messages.success(request, "Resmi tatil başarıyla silindi.")
    return redirect('mercis657:tanimlamalar')
