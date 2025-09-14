from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Bildirim, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin
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
    tarih = request.POST.get('tarih')
    aciklama = request.POST.get('aciklama', '').strip()

    if not tarih:
        messages.error(request, "Tarih alanı zorunludur.")
        return redirect('resmi_tatiller')

    if ResmiTatil.objects.filter(tarih=tarih).exists():
        messages.error(request, "Bu tarihe ait bir resmi tatil zaten mevcut.")
        return redirect('resmi_tatiller')

    ResmiTatil.objects.create(tarih=tarih, aciklama=aciklama)
    messages.success(request, "Resmi tatil başarıyla eklendi.")
    return redirect('resmi_tatiller')

@login_required
@require_POST
def tatil_duzenle(request):
    """ Mevcut resmi tatili düzenler """
    tatil_id = request.POST.get('tatil_id')
    tarih = request.POST.get('tarih')
    aciklama = request.POST.get('aciklama', '').strip()

    tatil = get_object_or_404(ResmiTatil, id=tatil_id)

    if not tarih:
        messages.error(request, "Tarih alanı zorunludur.")
        return redirect('resmi_tatiller')

    if ResmiTatil.objects.filter(tarih=tarih).exclude(id=tatil_id).exists():
        messages.error(request, "Bu tarihe ait başka bir resmi tatil zaten mevcut.")
        return redirect('resmi_tatiller')

    tatil.tarih = tarih
    tatil.aciklama = aciklama
    tatil.save()
    messages.success(request, "Resmi tatil başarıyla güncellendi.")
    return redirect('resmi_tatiller')

@login_required
@require_POST
def tatil_sil(request, tatil_id):
    """ Resmi tatili siler """
    tatil = get_object_or_404(ResmiTatil, id=tatil_id)
    tatil.delete()
    messages.success(request, "Resmi tatil başarıyla silindi.")
    return redirect('resmi_tatiller')
