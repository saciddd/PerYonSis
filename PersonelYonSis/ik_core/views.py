from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
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

def personel_list(request):
    query = Q()
    tc_kimlik_no = request.GET.get('tc_kimlik_no', '').strip()
    ad_soyad = request.GET.get('ad_soyad', '').strip()
    unvan = request.GET.get('unvan', '')
    telefon = request.GET.get('telefon', '').strip()

    if tc_kimlik_no:
        query &= Q(tc_kimlik_no__icontains=tc_kimlik_no)
    if ad_soyad:
        query &= (Q(ad__icontains=ad_soyad) | Q(soyad__icontains=ad_soyad))
    if unvan:
        query &= Q(unvan_id=unvan)
    if telefon:
        query &= Q(telefon__icontains=telefon)

    personeller = Personel.objects.filter(query).select_related('unvan', 'brans', 'kurum')
    unvanlar = Unvan.objects.all()

    return render(request, 'ik_core/personel_list.html', {
        'personeller': personeller,
        'unvanlar': unvanlar,
        'arama': {
            'tc_kimlik_no': tc_kimlik_no,
            'ad_soyad': ad_soyad,
            'unvan': unvan,
            'telefon': telefon,
        }
    })

@login_required
def personel_list_ajax(request):
    """Personel listesini DataTables için asenkron (server-side) döndürür."""
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))

    tc_kimlik_no = request.GET.get('tc_kimlik_no', '').strip()
    ad_soyad = request.GET.get('ad_soyad', '').strip()
    unvanlar = request.GET.getlist('unvan[]')
    kurumlar = request.GET.getlist('kurum[]')
    teskilatlar = request.GET.getlist('teskilat[]')

    queryset = Personel.objects.all()
    if tc_kimlik_no:
        queryset = queryset.filter(tc_kimlik_no__icontains=tc_kimlik_no)
    if ad_soyad:
        queryset = queryset.filter(
            Q(ad__icontains=ad_soyad) | Q(soyad__icontains=ad_soyad)
        )
    if unvanlar:
        queryset = queryset.filter(unvan_id__in=unvanlar)
    if kurumlar:
        queryset = queryset.filter(kurum_id__in=kurumlar)
    if teskilatlar:
        queryset = queryset.filter(teskilat__in=teskilatlar)

    total_count = queryset.count()
    queryset = queryset.select_related('unvan', 'brans', 'kurum')[start:start+length]

    data = []
    for p in queryset:
        data.append({
            "tc_kimlik_no": p.tc_kimlik_no,
            "ad": p.ad,
            "soyad": p.soyad,
            "unvan": p.unvan.ad if p.unvan else "",
            "brans": p.brans.ad if p.brans else "",
            "teskilat": p.teskilat,
            "kurum": p.kurum.ad if p.kurum else "",
            "durum": p.durum,
            "islemler": f'<a href="{reverse("ik_core:personel_detay", args=[p.pk])}" class="btn btn-info btn-sm">Detay</a>'
        })

    return JsonResponse({
        "draw": draw,
        "recordsTotal": total_count,
        "recordsFiltered": total_count,
        "data": data
    })

def personel_kontrol(request):
    """AJAX: T.C. Kimlik No ile sistemde kayıtlı personel var mı?"""
    tc = request.GET.get('tc_kimlik_no', '').strip()
    exists = Personel.objects.filter(tc_kimlik_no=tc).exists()
    return JsonResponse({'exists': exists})

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
    branslar = Brans.objects.all() # Consider filtering by unvan if needed dynamically
    kurumlar = Kurum.objects.all()
    ozel_durum_all = OzelDurum.objects.all()
    ozel_durumu_ids = list(personel.ozel_durumu.values_list('id', flat=True))

    # Use constants from valuelists
    teskilat_choices = TESKILAT_DEGERLERI
    mazeret_durumu_choices = MAZERET_DEGERLERI
    tahsil_durumu_choices = EGITIM_DEGERLERI
    cinsiyet_choices = Personel._meta.get_field('cinsiyet').choices # Get choices from model field
    ayrilma_nedeni_choices = AYRILMA_NEDENI_DEGERLERI
    vergi_indirimi_choices = ENGEL_DERECESI_DEGERLERI

    gecici_gorev_form = GeciciGorevForm(initial={
        'asil_kurumu': personel.kurum.ad if personel.kurum else ''
    })

    if request.method == 'POST':
        # Check if the save is for the main form or the separation form
        if 'save_main' in request.POST: # Assuming main save button has name="save_main"
            form = PersonelForm(request.POST, instance=personel)
            if form.is_valid():
                form.save()
                messages.success(request, f"{personel.ad_soyad} bilgileri başarıyla güncellendi.")
                return redirect('ik_core:personel_detay', pk=pk)
            else:
                messages.error(request, "Formda hatalar var. Lütfen kontrol ediniz.")
        elif 'save_ayrilis' in request.POST: # Assuming separation save button has name="save_ayrilis"
             # Only update separation fields
             personel.ayrilma_tarihi = request.POST.get('ayrilma_tarihi') or None
             personel.ayrilma_nedeni = request.POST.get('ayrilma_nedeni') or ''
             personel.ayrilma_detay = request.POST.get('ayrilma_detay') or ''
             try:
                 personel.save(update_fields=['ayrilma_tarihi', 'ayrilma_nedeni', 'ayrilma_detay'])
                 messages.success(request, f"{personel.ad_soyad} için ayrılış bilgileri kaydedildi.")
             except Exception as e:
                 messages.error(request, f"Ayrılış bilgileri kaydedilirken hata oluştu: {e}")
             return redirect('ik_core:personel_detay', pk=pk)
        # Handle other potential POST actions if needed

    # No need to pass the form instance if the template builds fields manually using 'personel' object
    context = {
        'personel': personel,
        'unvanlar': unvanlar,
        'branslar': branslar,
        'kurumlar': kurumlar, # Used for Kurum, Kadro Yeri, Fiili Görev Yeri selects
        'gecici_gorev_form': gecici_gorev_form,
        'teskilat_choices': teskilat_choices,
        'mazeret_durumu_choices': mazeret_durumu_choices,
        'tahsil_durumu_choices': tahsil_durumu_choices,
        'cinsiyet_choices': cinsiyet_choices,
        'ozel_durumu_choices': ozel_durum_all, # Pass all OzelDurum objects for the multi-select
        'ozel_durumu_ids': ozel_durumu_ids, # Pass selected IDs
        'ayrilma_nedeni_choices': ayrilma_nedeni_choices, # Add separation reason choices
        'vergi_indirimi_choices': vergi_indirimi_choices, # Add tax reduction choices
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
    return redirect(reverse('ik_core:personel_detay', args=[personel_id]))

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
