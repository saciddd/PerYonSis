from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Value as V
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.contrib import messages # Import messages framework
from django.contrib.auth.decorators import login_required
from .models.personel import Personel, Unvan, Brans, Kurum, OzelDurum # Import OzelDurum
from .models.GeciciGorev import GeciciGorev
# Import value lists needed
from .models.valuelists import (
    TESKILAT_DEGERLERI, EGITIM_DEGERLERI, MAZERET_DEGERLERI,
    AYRILMA_NEDENI_DEGERLERI, ENGEL_DERECESI_DEGERLERI # Add necessary value lists
)
from .forms import PersonelForm, KurumForm, UnvanForm, BransForm, GeciciGorevForm

@login_required
def personel_list(request):
    query = Q()
    tc_kimlik_no = request.GET.get('tc_kimlik_no', '').strip()
    ad_soyad = request.GET.get('ad_soyad', '').strip()
    telefon = request.GET.get('telefon', '').strip()
    unvan = request.GET.get('unvan', '')
    durum = request.GET.get('durum', '')

    # TC Kimlik no
    if tc_kimlik_no:
        query &= Q(tc_kimlik_no__icontains=tc_kimlik_no)

    # Ad-soyad
    if ad_soyad:
        parts = ad_soyad.split()
        if len(parts) == 1:
            query &= (Q(ad__icontains=parts[0]) | Q(soyad__icontains=parts[0]))
        else:
            query &= (Q(ad__icontains=parts[0]) & Q(soyad__icontains=parts[-1]))

    # Telefon
    if telefon:
        query &= Q(telefon__icontains=telefon)

    # Unvan
    if unvan:
        query &= Q(unvan_id=unvan)

    # Eğer hiç arama kriteri yoksa boş queryset döndür
    if not any([tc_kimlik_no, ad_soyad, telefon, unvan, durum]):
        personeller = Personel.objects.none()
    else:
        queryset = Personel.objects.filter(query).select_related('unvan', 'brans', 'kurum')
        if durum:
            personeller = [p for p in queryset if p.durum == durum]
        else:
            personeller = queryset

    unvanlar = Unvan.objects.all()

    return render(request, 'ik_core/personel_list.html', {
        'personeller': personeller,
        'unvanlar': unvanlar,
        'arama': {
            'tc_kimlik_no': tc_kimlik_no,
            'ad_soyad': ad_soyad,
            'telefon': telefon,
            'unvan': unvan,
            'durum': durum,
        }
    })

@login_required
def personel_kontrol(request):
    """AJAX: T.C. Kimlik No ile sistemde kayıtlı personel var mı?"""
    tc = request.GET.get('tc_kimlik_no', '').strip()
    exists = Personel.objects.filter(tc_kimlik_no=tc).exists()
    return JsonResponse({'exists': exists})

@login_required
def get_brans_by_unvan(request):
    """AJAX: Unvan ID'sine göre branşları getir"""
    unvan_id = request.GET.get('unvan_id')
    if unvan_id:
        branslar = Brans.objects.filter(unvan_id=unvan_id).values('id', 'ad')
        return JsonResponse({'branslar': list(branslar)})
    return JsonResponse({'branslar': []})

def personel_ekle(request):
    if request.method == 'POST':
        form = PersonelForm(request.POST)
        if form.is_valid():
            personel = form.save(commit=False)
            kadrolu = form.cleaned_data.get('kadrolu_personel')
            # Geçici görev alanlarını POST'tan al
            gecici_gorev_baslangic = request.POST.get('gecici_gorev_baslangic')
            gorevlendirildigi_birim = request.POST.get('gorevlendirildigi_birim')
            # Kişi kaydını oluştur
            personel.save()
            form.save_m2m()
            # Eğer kadrolu değilse otomatik geçici görev kaydı oluştur
            if not kadrolu and gecici_gorev_baslangic and gorevlendirildigi_birim:
                GeciciGorev.objects.create(
                    personel=personel,
                    gecici_gorev_baslangic=gecici_gorev_baslangic,
                    gorevlendirildigi_birim=gorevlendirildigi_birim
                )
            return redirect('ik_core:personel_list')
    else:
        form = PersonelForm()
    return render(request, 'ik_core/personel_ekle.html', {'form': form})

def personel_detay(request, pk):
    personel = get_object_or_404(Personel.objects.select_related('unvan', 'brans', 'kurum', 'kadro_yeri', 'fiili_gorev_yeri').prefetch_related('ozel_durumu', 'gecicigorev_set'), pk=pk)
    unvanlar = Unvan.objects.all()
    branslar = Brans.objects.all()
    kurumlar = Kurum.objects.all()
    ozel_durum_all = OzelDurum.objects.all()
    ozel_durumu_ids = list(personel.ozel_durumu.values_list('id', flat=True))

    # Use constants from valuelists
    teskilat_choices = TESKILAT_DEGERLERI
    mazeret_durumu_choices = MAZERET_DEGERLERI
    tahsil_durumu_choices = EGITIM_DEGERLERI
    cinsiyet_choices = Personel._meta.get_field('cinsiyet').choices
    ayrilma_nedeni_choices = AYRILMA_NEDENI_DEGERLERI
    vergi_indirimi_choices = ENGEL_DERECESI_DEGERLERI

    gecici_gorev_form = GeciciGorevForm(initial={
        'asil_kurumu': personel.kurum.ad if personel.kurum else ''
    })

    # PersonelForm instance'ını oluştur
    form = PersonelForm(instance=personel)

    if request.method == 'POST':
        if 'save_main' in request.POST:
            form = PersonelForm(request.POST, instance=personel)
            if form.is_valid():
                form.save()
                messages.success(request, f"{personel.ad} {personel.soyad} bilgileri başarıyla güncellendi.")
                return redirect('ik_core:personel_detay', pk=pk)
            else:
                messages.error(request, "Formda hatalar var. Lütfen kontrol ediniz.")
        elif 'save_ayrilis' in request.POST:
            # Ayrılış bilgilerini güncelle
            personel.ayrilma_tarihi = request.POST.get('ayrilma_tarihi') or None
            personel.ayrilma_nedeni = request.POST.get('ayrilma_nedeni') or ''
            personel.ayrilma_detay = request.POST.get('ayrilma_detay') or ''
            try:
                personel.save(update_fields=['ayrilma_tarihi', 'ayrilma_nedeni', 'ayrilma_detay'])
                messages.success(request, f"{personel.ad} {personel.soyad} için ayrılış bilgileri kaydedildi.")
            except Exception as e:
                messages.error(request, f"Ayrılış bilgileri kaydedilirken hata oluştu: {e}")
            return redirect('ik_core:personel_detay', pk=pk)

    context = {
        'personel': personel,
        'form': form,  # PersonelForm instance'ını context'e ekle
        'unvanlar': unvanlar,
        'branslar': branslar,
        'kurumlar': kurumlar,
        'gecici_gorev_form': gecici_gorev_form,
        'teskilat_choices': teskilat_choices,
        'mazeret_durumu_choices': mazeret_durumu_choices,
        'tahsil_durumu_choices': tahsil_durumu_choices,
        'cinsiyet_choices': cinsiyet_choices,
        'ozel_durumu_choices': ozel_durum_all,
        'ozel_durumu_ids': ozel_durumu_ids,
        'ayrilma_nedeni_choices': ayrilma_nedeni_choices,
        'vergi_indirimi_choices': vergi_indirimi_choices,
    }
    return render(request, 'ik_core/personel_detay.html', context)

@require_POST
def gecici_gorev_ekle(request, personel_id):
    personel = get_object_or_404(Personel, pk=personel_id)
    form = GeciciGorevForm(request.POST)
    if form.is_valid():
        gecici_gorev = form.save(commit=False)
        gecici_gorev.personel = personel
        gecici_gorev.save()
        messages.success(request, f"{personel.ad} {personel.soyad} için geçici görev kaydı başarıyla eklendi.")
    return JsonResponse({
        'success': True,
    })

@require_POST
def gecici_gorev_sil(request, personel_id, gorev_id):
    personel = get_object_or_404(Personel, pk=personel_id)
    gorev = get_object_or_404(personel.gecicigorev_set, pk=gorev_id)
    gorev.delete()
    return redirect(reverse('ik_core:personel_detay', args=[personel_id]))

def personel_duzenle(request, pk):
    personel = get_object_or_404(Personel, pk=pk)
    if request.method == 'POST':
        form = PersonelForm(request.POST, instance=personel)
        if form.is_valid():
            form.save()
            return redirect('ik_core:personel_detay', pk=pk)
    else:
        form = PersonelForm(instance=personel)
    return render(request, 'ik_core/personel_duzenle.html', {'form': form, 'personel': personel})

def kurum_tanimlari(request):
    kurumlar = Kurum.objects.all()
    if request.method == 'POST':
        form = KurumForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ik_core:kurum_tanimlari')
    else:
        form = KurumForm()
    return render(request, 'ik_core/kurum_tanimlari.html', {'kurumlar': kurumlar, 'form': form})

def unvan_branstanimlari(request):
    unvanlar = Unvan.objects.all()
    selected_unvan_id = request.GET.get('unvan_id')
    selected_unvan = None
    branslar = Brans.objects.none()
    if selected_unvan_id:
        selected_unvan = get_object_or_404(Unvan, id=selected_unvan_id)
        branslar = Brans.objects.filter(unvan=selected_unvan)
    if request.method == 'POST':
        if 'unvan_ekle' in request.POST:
            unvan_form = UnvanForm(request.POST, prefix='unvan')
            if unvan_form.is_valid():
                unvan_form.save()
                return redirect('ik_core:unvan_branstanimlari')
        elif 'brans_ekle' in request.POST:
            brans_form = BransForm(request.POST, prefix='brans')
            if brans_form.is_valid():
                brans_form.save()
                return redirect(f"{request.path}?unvan_id={brans_form.cleaned_data['unvan'].id}")
    else:
        unvan_form = UnvanForm(prefix='unvan')
        brans_form = BransForm(prefix='brans')
    return render(request, 'ik_core/unvan_branstanimlari.html', {
        'unvanlar': unvanlar,
        'selected_unvan': selected_unvan,
        'branslar': branslar,
        'unvan_form': unvan_form,
        'brans_form': brans_form,
    })

def tanimlamalar(request):
    return render(request, 'ik_core/tanimlamalar.html')

# Placeholder view for Ilisik Kesme Formu
def ilisik_kesme_formu(request, pk):
    personel = get_object_or_404(Personel, pk=pk)
    # TODO: Implement the logic for generating/displaying the form
    context = {
        'personel': personel,
        # Add any other context needed for the form
    }
    # Replace 'ik_core/ilisik_kesme_formu.html' with the actual template path
    return render(request, 'ik_core/ilisik_kesme_formu_placeholder.html', context)
