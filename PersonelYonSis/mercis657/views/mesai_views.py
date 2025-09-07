from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Mesai_Tanimlari
from datetime import timedelta


def mesai_tanimlari(request):
    mesai_tanimlari = Mesai_Tanimlari.objects.all()
    return render(request, 'mercis657/mesai_tanimlari.html', {"mesai_tanimlari": mesai_tanimlari})
# Yeni Mesai Tanımı Ekleme Fonksiyonu
def add_mesai_tanim(request):
    if request.method == 'POST':
        # Formdan gelen verileri alıyoruz
        saat = request.POST.get('Saat')
        gunduz_mesaisi = request.POST.get('GunduzMesaisi') == 'on'
        aksam_mesaisi = request.POST.get('AksamMesaisi') == 'on'
        gece_mesaisi = request.POST.get('GeceMesaisi') == 'on'
        ise_geldi = request.POST.get('IseGeldi') == 'on'
        sonraki_gune_sarkiyor = request.POST.get('SonrakiGuneSarkiyor') == 'on'
        ara_dinlenme = request.POST.get('AraDinlenme')
        gecerli_mesai = request.POST.get('GecerliMesai') == 'on'
        ckys_btf_karsiligi = request.POST.get('CKYS_BTF_Karsiligi')

        # Ara dinlenme süresini timedelta nesnesine dönüştürme
        if ara_dinlenme:
            hours, minutes = map(int, ara_dinlenme.split(':'))
            ara_dinlenme_td = timedelta(hours=hours, minutes=minutes)
        else:
            ara_dinlenme_td = None

        # Yeni mesai tanımı oluşturma
        yeni_mesai = Mesai_Tanimlari(
            Saat=saat,
            GunduzMesaisi=gunduz_mesaisi,
            AksamMesaisi=aksam_mesaisi,
            GeceMesaisi=gece_mesaisi,
            IseGeldi=ise_geldi,
            SonrakiGuneSarkiyor=sonraki_gune_sarkiyor,
            AraDinlenme=ara_dinlenme_td,
            GecerliMesai=gecerli_mesai,
            CKYS_BTF_Karsiligi=ckys_btf_karsiligi
        )
        
        # Mesai süresini hesaplayarak kaydet
        yeni_mesai.calculate_sure()
        yeni_mesai.save()

        return redirect('mercis657:mesai_tanimlari')  # İşlem tamamlandığında liste sayfasına yönlendirme

    return render(request, 'mesai_tanimlari.html')

def mesai_tanim_update(request):
    mesai_id = request.POST.get('mesai_id')
    mesai = get_object_or_404(Mesai_Tanimlari, id=mesai_id)
    
    if request.method == 'POST':
        try:
            # Formdan gelen güncellenmiş verileri alıyoruz
            mesai.Saat = request.POST.get('saat')
            mesai.GunduzMesaisi = request.POST.get('GunduzMesaisi') == 'on'
            mesai.AksamMesaisi = request.POST.get('AksamMesaisi') == 'on'
            mesai.GeceMesaisi = request.POST.get('GeceMesaisi') == 'on'
            mesai.IseGeldi = request.POST.get('IseGeldi') == 'on'
            mesai.SonrakiGuneSarkiyor = request.POST.get('SonrakiGuneSarkiyor') == 'on'
            ara_dinlenme = request.POST.get('AraDinlenme')
            mesai.AraDinlenme = ara_dinlenme if ara_dinlenme else None
            mesai.GecerliMesai = request.POST.get('GecerliMesai') == 'on'
            mesai.CKYS_BTF_Karsiligi = request.POST.get('CKYS_BTF_Karsiligi')

            mesai.save()  # Güncellenmiş verileri kaydet
            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})
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
