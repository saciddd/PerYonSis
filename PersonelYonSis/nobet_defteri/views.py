from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponseForbidden, JsonResponse
from .models import NobetDefteri, NobetTuru, NobetOlayKaydi
from .forms import NobetDefteriForm, NobetOlayKaydiForm
from PersonelYonSis.views import get_user_permissions
from django.contrib.auth import get_user_model
User = get_user_model()

# Nöbet defteri listesi
def nobet_defteri_list(request):
    defterler = NobetDefteri.objects.all().order_by('-tarih', '-created_at')
    onay_yetkisi = 'Nöbet Defteri Onaylayabilir' in get_user_permissions(request.user)
    # onay_yetkisi = request.user.has_permission('Nöbet Defteri Onaylayabilir')
    return render(request, 'nobet_defteri/list.html', {'defterler': defterler, 'onay_yetkisi': onay_yetkisi})

# Yeni nöbet defteri oluştur
def nobet_defteri_olustur(request):
    if not request.user.has_permission('Nöbet Defteri Oluşturabilir'):
        return HttpResponseForbidden("Nöbet defteri oluşturma yetkiniz yok.")

    error_message = None

    if request.method == 'POST':
        form = NobetDefteriForm(request.POST)
        if form.is_valid():
            defter = form.save(commit=False)
            defter.olusturan = request.user
            defter.save()
            messages.success(request, "Nöbet defteri başarıyla oluşturuldu.")
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True})
            return redirect('nobet_defteri:detay', defter.id)
        else:
            # Çakışma veya diğer form hataları burada
            hata = "; ".join(form.non_field_errors())
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "error": hata or "Form geçersiz."})
            messages.error(request, hata or "Form geçersiz.")
            return redirect('nobet_defteri:liste')
    else:
        form = NobetDefteriForm()

    if request.GET.get("modal"):
        return render(request, "nobet_defteri/olustur.html", {"form": form, "error_message": error_message})
    return redirect('nobet_defteri:liste')

# Defter detayı ve olaylar
def nobet_defteri_detay(request, defter_id):
    defter = get_object_or_404(NobetDefteri, id=defter_id)
    olaylar = defter.olaylar.order_by('saat')

    if request.method == 'POST':
        if not request.user.has_permission('Nöbet Olayı Ekleyebilir'):
            return HttpResponseForbidden("Olay ekleme yetkiniz yok.")
        form = NobetOlayKaydiForm(request.POST)
        if form.is_valid():
            olay = form.save(commit=False)
            olay.defter = defter
            olay.ekleyen = request.user
            olay.save()
            messages.success(request, "Olay kaydı eklendi.")
            return redirect('nobet_defteri:detay', defter.id)
    else:
        form = NobetOlayKaydiForm()

    return render(request, 'nobet_defteri/detay.html', {
        'defter': defter,
        'olaylar': olaylar,
        'form': form
    })

# Nöbet defteri onayla
def nobet_defteri_onayla(request, defter_id):
    if not request.user.has_permission('Nöbet Defteri Onaylayabilir'):
        return HttpResponseForbidden("Nöbet defteri onaylama yetkiniz yok.")

    defter = get_object_or_404(NobetDefteri, id=defter_id)
    defter.onayli = True
    defter.onaylayan = request.user
    defter.onay_tarihi = now()
    defter.save()
    messages.success(request, "Nöbet defteri onaylandı.")
    return redirect('nobet_defteri:liste')

def nobet_defteri_olaylar_modal(request, defter_id):
    defter = get_object_or_404(NobetDefteri, id=defter_id)
    olaylar = defter.olaylar.all().order_by('-eklenme_zamani')
    return render(request, "nobet_defteri/olaylar_modal.html", {
        "olaylar": olaylar,
        "defter": defter,
    })
    defter.save()
    messages.success(request, "Nöbet defteri onaylandı.")
    return redirect('nobet_defteri:liste')

def nobet_defteri_olaylar_modal(request, defter_id):
    defter = get_object_or_404(NobetDefteri, id=defter_id)
    olaylar = defter.olaylar.all().order_by('-eklenme_zamani')
    return render(request, "nobet_defteri/olaylar_modal.html", {
        "olaylar": olaylar,
        "defter": defter,
    })
