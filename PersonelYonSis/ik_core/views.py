from django.shortcuts import render, get_object_or_404, redirect
from django.db.models.query import QuerySet
from django.db.models import Q, Value as V
from django.db.models.functions import Lower, Concat
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string, get_template
import pdfkit
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages # Import messages framework
from django.contrib.auth.decorators import login_required
from .models.personel import Personel, Unvan, Brans, Kurum, OzelDurum # Import OzelDurum
from .models.GeciciGorev import GeciciGorev
from .models import UstBirim, Bina, Birim, PersonelBirim
# Import value lists needed
from .models.valuelists import (
    TESKILAT_DEGERLERI, EGITIM_DEGERLERI, MAZERET_DEGERLERI,
    AYRILMA_NEDENI_DEGERLERI, ENGEL_DERECESI_DEGERLERI # Add necessary value lists
)
from .forms import PersonelForm, KurumForm, UnvanForm, BransForm, GeciciGorevForm
from django.db import models
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET
from django.forms import ModelForm
from .models.Teblig import TebligImzasi, TebligMetni

# Türkçe lower/upper normalize edici yardımcı
def lower_tr(text: str) -> str:
    """
    Türkçe küçük harf dönüşümü.
    Normal .lower() "I/İ/ı/i" harflerinde sorun çıkarabilir.
    """
    if not text:
        return text
    return (text
        .replace("I", "ı")
        .replace("İ", "i")
        .lower()
    )

@login_required
def personel_list(request):
    query = Q()
    tc_kimlik_no = request.GET.get('tc_kimlik_no', '').strip()
    ad_soyad = request.GET.get('ad_soyad', '').strip()
    telefon = request.GET.get('telefon', '').strip()
    # Çoklu unvan desteği: aynı isimle birden fazla parametre gelebilir
    unvan_list = request.GET.getlist('unvan')
    durum = request.GET.get('durum', '')

    if tc_kimlik_no:
        query &= Q(tc_kimlik_no__icontains=tc_kimlik_no)

    if ad_soyad:
        ad_soyad_norm = lower_tr(ad_soyad)
        # Lower fonksiyonuyla veritabanı tarafında normalize et
        query &= (
            Q(ad__isnull=False) & Q(ad__icontains=ad_soyad_norm) |
            Q(soyad__isnull=False) & Q(soyad__icontains=ad_soyad_norm)
        )

    if telefon:
        query &= Q(telefon__icontains=telefon)
    if unvan_list:
        query &= Q(unvan_id__in=unvan_list)

    if not any([tc_kimlik_no, ad_soyad, telefon, unvan_list, durum]):
        personeller = Personel.objects.none()
    else:
        queryset = Personel.objects.annotate(
            ad_lower=Lower('ad'),
            soyad_lower=Lower('soyad')
        ).filter(query).select_related('unvan', 'brans', 'kurum')

        if durum:
            # 'durum' model alanı değil (property), DB tarafında filtrelenemez.
            # Kullanıcı 'Aktif' veya 'Pasif' seçmişse, property değerinin bu kelimeyle başlamasını kabul edelim.
            if durum in ("Aktif", "Pasif"):
                personeller = [p for p in queryset if (p.durum or "").startswith(durum)]
            else:
                personeller = [p for p in queryset if p.durum == durum]
        else:
            personeller = queryset

    unvanlar = Unvan.objects.all()

    return render(request, 'ik_core/personel_list.html', {
        'personeller': personeller,
        'personel_sayisi': personeller.count() if isinstance(personeller, QuerySet) else len(personeller),
        'unvanlar': unvanlar,
        'arama': {
            'tc_kimlik_no': tc_kimlik_no,
            'ad_soyad': ad_soyad,
            'telefon': telefon,
            'unvan': unvan_list,
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
    
    # Personelin en son çalıştığı birim bilgisini al
    son_birim_kaydi = PersonelBirim.objects.filter(personel=personel).order_by('-gecis_tarihi', '-creation_timestamp').first()
    
    # Personelin birim geçmişi
    personel_birim_gecmisi = PersonelBirim.objects.filter(personel=personel).order_by('-gecis_tarihi', '-creation_timestamp')
    
    # Modal'lar için gerekli veriler
    ust_birimler = UstBirim.objects.all().order_by('ad')
    binalar = Bina.objects.all().order_by('ad')
    teblig_imzalari = TebligImzasi.objects.all().order_by('ad')

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
            # POST verilerini işle ve eksik alanları doldur
            post_data = request.POST.copy()
            
            # Eğer hidden input'lardan gelen değerler varsa, onları kullan
            # Aksi halde mevcut personel değerlerini kullan
            if not post_data.get('tc_kimlik_no'):
                post_data['tc_kimlik_no'] = personel.tc_kimlik_no
            if not post_data.get('ad'):
                post_data['ad'] = personel.ad
            if not post_data.get('soyad'):
                post_data['soyad'] = personel.soyad
            if not post_data.get('kurum'):
                post_data['kurum'] = personel.kurum.id if personel.kurum else ''
            
            form = PersonelForm(post_data, instance=personel)
            if form.is_valid():
                form.save()
                messages.success(request, f"{personel.ad} {personel.soyad} bilgileri başarıyla güncellendi.")
                return redirect('ik_core:personel_detay', pk=pk)
            else:
                # Form hatalarını detaylı olarak logla
                print("=== FORM HATALARI DEBUG ===")
                print(f"POST verileri: {request.POST}")
                print("İşlenmiş POST verileri: {post_data}")
                print("Form hataları:")
                for field, errors in form.errors.items():
                    print(f"  {field}: {errors}")
                
                # Form alanlarının değerlerini kontrol et
                print("Form alanları değerleri:")
                for field_name, field in form.fields.items():
                    value = form.data.get(field_name, 'BOŞ')
                    print(f"  {field_name}: {value}")
                
                # Hata mesajlarını kullanıcıya göster
                error_messages = []
                for field, errors in form.errors.items():
                    field_name = form.fields[field].label if hasattr(form.fields[field], 'label') else field
                    for error in errors:
                        error_messages.append(f"{field_name}: {error}")
                
                if error_messages:
                    messages.error(request, f"Formda hatalar var: {'; '.join(error_messages)}")
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
        'son_birim_kaydi': son_birim_kaydi,
        'personel_birim_gecmisi': personel_birim_gecmisi,
        'ust_birimler': ust_birimler,
        'binalar': binalar,
        'teblig_imzalari': teblig_imzalari,
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
                messages.success(request, f"{unvan_form.cleaned_data['ad']} unvanı tanımlandı")
                return redirect('ik_core:unvan_branstanimlari')
        elif 'brans_ekle' in request.POST:
            brans_form = BransForm(request.POST, prefix='brans')
            if brans_form.is_valid():
                brans_form.save()
                messages.success(request, f"{brans_form.cleaned_data['ad']} branşı tanımlandı")
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

# =====================
# Tebliğ: Modeller için basit formlar
# =====================

class TebligImzasiForm(ModelForm):
    class Meta:
        model = TebligImzasi
        fields = ['ad', 'metin']


class TebligMetniForm(ModelForm):
    class Meta:
        model = TebligMetni
        fields = ['ad', 'metin']


# =====================
# Tebliğ: Tanım sayfaları ve CRUD
# =====================

@login_required
def imza_tanimlari(request):
    imzalar = TebligImzasi.objects.order_by('ad')
    form = TebligImzasiForm()
    return render(request, 'ik_core/imza_tanimlari.html', {
        'imzalar': imzalar,
        'form': form,
    })


@login_required
def teblig_tanimlari(request):
    tebligler = TebligMetni.objects.order_by('ad')
    form = TebligMetniForm()
    return render(request, 'ik_core/teblig_tanimlari.html', {
        'tebligler': tebligler,
        'form': form,
    })


@login_required
@require_POST
def teblig_imzasi_ekle(request):
    pk = request.POST.get('id')
    if pk:
        instance = get_object_or_404(TebligImzasi, pk=pk)
        form = TebligImzasiForm(request.POST, instance=instance)
    else:
        form = TebligImzasiForm(request.POST)
    if form.is_valid():
        imza = form.save()
        return JsonResponse({'success': True, 'id': imza.id, 'ad': imza.ad, 'metin': imza.metin})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def teblig_imzasi_sil(request, pk):
    imza = get_object_or_404(TebligImzasi, pk=pk)
    imza.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def teblig_metni_ekle(request):
    pk = request.POST.get('id')
    if pk:
        instance = get_object_or_404(TebligMetni, pk=pk)
        form = TebligMetniForm(request.POST, instance=instance)
    else:
        form = TebligMetniForm(request.POST)
    if form.is_valid():
        tm = form.save()
        return JsonResponse({'success': True, 'id': tm.id, 'ad': tm.ad, 'metin': tm.metin})
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def teblig_metni_sil(request, pk):
    tm = get_object_or_404(TebligMetni, pk=pk)
    tm.delete()
    return JsonResponse({'success': True})


# =====================
# Tebliğ: İşlemleri Sayfası
# =====================

@login_required
def teblig_islemleri(request, personel_id: int):
    personel = get_object_or_404(Personel, pk=personel_id)
    imzalar = TebligImzasi.objects.order_by('ad')
    tebligler = TebligMetni.objects.order_by('ad')
    return render(request, 'ik_core/teblig_islemleri.html', {
        'personel': personel,
        'imzalar': imzalar,
        'tebligler': tebligler,
    })


@login_required
@require_POST
def teblig_metni_guncelle(request, pk: int):
    tm = get_object_or_404(TebligMetni, pk=pk)
    metin = request.POST.get('metin', '')
    tm.metin = metin
    tm.save(update_fields=['metin'])
    return JsonResponse({'success': True})


@login_required
@require_GET
def teblig_metni_get(request, pk: int):
    tm = get_object_or_404(TebligMetni, pk=pk)
    return JsonResponse({'id': tm.id, 'ad': tm.ad, 'metin': tm.metin})

# Placeholder view for Ilisik Kesme Formu
def ilisik_kesme_formu(request, pk):
    # Prepare PDF-specific context using the supplied PDF template (ilisik_kesme_formu.html)
    try:
        file_url = f"file:///{staticfiles_storage.path('logo/kdh_logo.png')}"
    except Exception:
        file_url = None
    
    personel = get_object_or_404(Personel, pk=pk)
    
    # prepare context matching the PDF template
    context_pdf = {
        'dokuman_kodu': 'KU.FR.31',
        'form_adi': 'İlişik Kesme Formu',
        'yayin_tarihi': 'Mayıs 2023',
        'kurum': 'KAYSERİ DEVLET HASTANESİ',
        'revizyon_tarihi': '-',
        'revizyon_no': '0',
        'sayfa_no': '1',
        'pdf_logo': file_url,
        'personel': personel,
    }

    # Render PDF template and generate PDF (landscape)
    try:
        template = get_template('ik_core/pdf/ilisik_kesme_formu.html')
        html = template.render({**context_pdf})
    except Exception:
        html = render_to_string('ik_core/pdf/ilisik_kesme_formu.html', context_pdf)

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'page-size': 'A4',
        'orientation': 'Portrait',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': '',
        'enable-external-links': True,
        'quiet': ''
    }

    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"ilisik_kesme_formu_{personel.ad_soyad}.pdf"
    filename = filename.replace(' ', '_')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

@require_http_methods(["POST"])
def ayrilis_kaydet(request, pk):
    """Ayrılış bilgilerini kaydet"""
    if request.method == 'POST':
        try:
            personel = get_object_or_404(Personel, pk=pk)
            
            # Ayrılış bilgilerini al
            ayrilma_tarihi = request.POST.get('ayrilma_tarihi')
            ayrilma_nedeni = request.POST.get('ayrilma_nedeni')
            ayrilma_detay = request.POST.get('ayrilma_detay', '')
            
            # Validasyon
            if not ayrilma_tarihi:
                return JsonResponse({
                    'success': False,
                    'message': 'Ayrılma tarihi zorunludur.'
                })
            
            if not ayrilma_nedeni:
                return JsonResponse({
                    'success': False,
                    'message': 'Ayrılma nedeni seçilmelidir.'
                })
            
            # Personel bilgilerini güncelle
            personel.ayrilma_tarihi = ayrilma_tarihi
            personel.ayrilma_nedeni = ayrilma_nedeni
            personel.ayrilma_detay = ayrilma_detay
            personel.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Ayrılış bilgileri başarıyla kaydedildi.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Geçersiz istek.'
    })

@require_http_methods(["POST"])
def personeli_aktiflestir(request, pk):
    """Personeli aktifleştir - ayrılış bilgilerini temizle"""
    if request.method == 'POST':
        try:
            personel = get_object_or_404(Personel, pk=pk)
            
            # Ayrılış bilgilerini temizle
            personel.ayrilma_tarihi = None
            personel.ayrilma_nedeni = None
            personel.ayrilma_detay = None
            personel.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Personel başarıyla aktifleştirildi.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Geçersiz istek.'
    })

@require_http_methods(["POST"])
def mazeret_sil(request, pk):
    """İlgili personel için mazeret kaydını sil"""
    if request.method == 'POST':
        try:
            personel = get_object_or_404(Personel, pk=pk)
            personel.mazeret_durumu = None
            personel.mazeret_baslangic = None
            personel.mazeret_bitis = None
            personel.save()
            return JsonResponse({
                'success': True,
                'message': 'Mazeret kaydı silindi.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Hata oluştu: {str(e)}'
            })
    return JsonResponse({
        'success': False,
        'message': 'Geçersiz istek.'
    })    

# =====================
# Geçici Görevler Sayfası
# =====================

@login_required
def gecici_gorevler(request):
    """
    RFC-001-GeciciGorevSayfasi gereksinimlerine uygun liste ve modal sayfası
    - Tarih filtresi ile o günü kapsayan kayıtlar
    - Sağ üstte modal açan buton
    """
    tarih_str = request.GET.get('tarih')
    kayitlar = []
    from .models.GeciciGorev import GeciciGorev
    if tarih_str:
        tarih = parse_date(tarih_str)
        if tarih:
            kayitlar = (GeciciGorev.objects
                        .filter(gecici_gorev_baslangic__lte=tarih)
                        .filter(models.Q(gecici_gorev_bitis__isnull=True) | models.Q(gecici_gorev_bitis__gte=tarih))
                        .select_related('personel'))
    kurumlar = Kurum.objects.order_by('ad').all()
    return render(request, 'ik_core/gecici_gorevler.html', {
        'kayitlar': kayitlar,
        'tarih': tarih_str or '',
        'kurumlar': kurumlar,
    })


@login_required
@require_POST
def gecici_gorev_bulk_kaydet(request):
    """
    Excel'den yapıştırılan satırlar için toplu kayıt oluşturma.
    Beklenen JSON body:
    {
      "kurum": "KAYSERİ DEVLET HASTANESİ",
      "satirlar": [
        {
          "tc": "123...",
          "sicil": "...",
          "ad": "...",
          "soyad": "...",
          "unvan": "...",
          "brans": "...",
          "kadro_birim": "...",
          "aktif_birim": "...",
          "baslangic": "YYYY-MM-DD",
          "bitis": "YYYY-MM-DD|null"
        }
      ]
    }
    Tip belirleme:
      - kurum == kadro_birim -> Gidis
      - kurum == aktif_birim -> Gelis
    """
    import json
    import re
    from datetime import datetime
    from .models.GeciciGorev import GeciciGorev

    def normalize_text(value: str) -> str:
        if value is None:
            return ''
        v = str(value).strip()
        # Baş/son tırnakları kaldır
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        # CR/LF -> boşluk, birden fazla boşluğu tek boşluk yap
        v = re.sub(r"\s+", " ", v.replace("\r", " ").replace("\n", " ")).strip()
        return v

    def upper_norm(value: str) -> str:
        return normalize_text(value).upper()

    def parse_any_date(value: str):
        if not value:
            return None
        s = normalize_text(value)
        # Doğrudan ISO (yyyy-mm-dd)
        d = parse_date(s)
        if d:
            return d
        # dd.mm.yyyy | d.mm.yyyy | dd/mm/yyyy | dd-mm-yyyy
        s2 = s.replace('/', '.').replace('-', '.')
        parts = s2.split('.')
        if len(parts) == 3 and parts[2].isdigit():
            try:
                day = parts[0].zfill(2)
                month = parts[1].zfill(2)
                year = parts[2]
                return datetime.strptime(f"{day}.{month}.{year}", "%d.%m.%Y").date()
            except Exception:
                pass
        # yyyy.mm.dd
        if len(parts) == 3 and parts[0].isdigit() and len(parts[0]) == 4:
            try:
                year = parts[0]
                month = parts[1].zfill(2)
                day = parts[2].zfill(2)
                return datetime.strptime(f"{year}.{month}.{day}", "%Y.%m.%d").date()
            except Exception:
                pass
        return None
    body = json.loads(request.body or '{}')
    kurum_adi = body.get('kurum')
    satirlar = body.get('satirlar', [])

    sayac_gelis = 0
    sayac_gidis = 0
    sayac_atlanan = 0

    for s in satirlar:
        tc = normalize_text(s.get('tc') or '')
        kadro_birim = normalize_text(s.get('kadro_birim') or '')
        aktif_birim = normalize_text(s.get('aktif_birim') or '')
        baslangic = parse_any_date(s.get('baslangic') or '')
        bitis = parse_any_date(s.get('bitis') or '') if s.get('bitis') else None
        if not tc or not baslangic:
            sayac_atlanan += 1
            continue
        try:
            personel = Personel.objects.get(tc_kimlik_no=tc)
        except Personel.DoesNotExist:
            sayac_atlanan += 1
            continue

        gorev_tipi = None
        if kurum_adi and upper_norm(kurum_adi) == upper_norm(kadro_birim):
            gorev_tipi = 'Gidis'
        if kurum_adi and upper_norm(kurum_adi) == upper_norm(aktif_birim):
            # aktif eşleşme varsa geliş öncelik kazansın
            gorev_tipi = 'Gelis'
        if gorev_tipi is None:
            sayac_atlanan += 1
            continue

        GeciciGorev.objects.create(
            personel=personel,
            gecici_gorev_tipi=gorev_tipi,
            gecici_gorev_baslangic=baslangic,
            gecici_gorev_bitis=bitis,
            asil_kurumu=kadro_birim,
            gorevlendirildigi_birim=aktif_birim,
        )
        if gorev_tipi == 'Gelis':
            sayac_gelis += 1
        else:
            sayac_gidis += 1

    return JsonResponse({
        'success': True,
        'message': (
            f"Geçici Görev kayıtları tamamlandı: {sayac_gelis} geliş, {sayac_gidis} gidiş. "
            f"{sayac_atlanan} satır atlandı."
        )
    })

@login_required
def birim_yonetimi(request):
    """Birim yönetimi sayfası - unvan_branstanimlari.html benzeri yapı"""
    binalar = Bina.objects.all().order_by('ad')
    ust_birimler = UstBirim.objects.all().order_by('ad')
    selected_bina_id = request.GET.get('bina_id')
    selected_bina = None
    birimler = []
    
    if selected_bina_id:
        selected_bina = get_object_or_404(Bina, id=selected_bina_id)
        birimler = Birim.objects.filter(bina=selected_bina).order_by('ust_birim__ad', 'ad')
    
    context = {
        'binalar': binalar,
        'ust_birimler': ust_birimler,
        'selected_bina': selected_bina,
        'birimler': birimler,
    }
    return render(request, 'ik_core/birim_yonetimi.html', context)

@login_required
@require_POST
def bina_ekle(request):
    """Bina ekleme endpoint'i"""
    ad = request.POST.get('ad', '').strip()
    if not ad:
        return JsonResponse({'success': False, 'message': 'Bina adı gereklidir.'})
    
    if Bina.objects.filter(ad=ad).exists():
        return JsonResponse({'success': False, 'message': 'Bu bina adı zaten mevcut.'})
    
    bina = Bina.objects.create(ad=ad)
    return JsonResponse({
        'success': True, 
        'message': 'Bina başarıyla eklendi.',
        'bina': {'id': bina.id, 'ad': bina.ad, 'birim_sayisi': 0}
    })

@login_required
@require_POST
def ust_birim_ekle(request):
    """Üst birim ekleme endpoint'i"""
    ad = request.POST.get('ad', '').strip()
    if not ad:
        return JsonResponse({'success': False, 'message': 'Üst birim adı gereklidir.'})
    
    if UstBirim.objects.filter(ad=ad).exists():
        return JsonResponse({'success': False, 'message': 'Bu üst birim adı zaten mevcut.'})
    
    ust_birim = UstBirim.objects.create(ad=ad)
    return JsonResponse({
        'success': True, 
        'message': 'Üst birim başarıyla eklendi.',
        'ust_birim': {'id': ust_birim.id, 'ad': ust_birim.ad}
    })

@login_required
@require_POST
def birim_ekle(request):
    """Birim ekleme endpoint'i"""
    bina_id = request.POST.get('bina_id')
    ust_birim_id = request.POST.get('ust_birim_id')
    ad = request.POST.get('ad', '').strip()
    
    if not all([bina_id, ust_birim_id, ad]):
        return JsonResponse({'success': False, 'message': 'Tüm alanlar gereklidir.'})
    
    try:
        bina = Bina.objects.get(id=bina_id)
        ust_birim = UstBirim.objects.get(id=ust_birim_id)
    except (Bina.DoesNotExist, UstBirim.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Geçersiz bina veya üst birim.'})
    
    if Birim.objects.filter(bina=bina, ad=ad).exists():
        return JsonResponse({'success': False, 'message': 'Bu birim adı bu binada zaten mevcut.'})
    
    birim = Birim.objects.create(bina=bina, ust_birim=ust_birim, ad=ad)
    return JsonResponse({
        'success': True, 
        'message': 'Birim başarıyla eklendi.',
        'birim': {
            'id': birim.id, 
            'ad': birim.ad, 
            'bina_ad': birim.bina.ad,
            'ust_birim_ad': birim.ust_birim.ad
        }
    })

@login_required
def get_birimler_by_bina(request):
    """Bina seçimine göre birimleri getiren AJAX endpoint'i"""
    bina_id = request.GET.get('bina_id')
    ust_birim_id = request.GET.get('ust_birim_id')
    
    if not bina_id:
        return JsonResponse({'birimler': []})
    
    birimler = Birim.objects.filter(bina_id=bina_id)
    if ust_birim_id:
        birimler = birimler.filter(ust_birim_id=ust_birim_id)
    
    birimler = birimler.order_by('ust_birim__ad', 'ad')
    
    return JsonResponse({
        'birimler': [
            {'id': birim.id, 'ad': birim.ad, 'ust_birim_ad': birim.ust_birim.ad}
            for birim in birimler
        ]
    })

@login_required
@require_POST
def personel_birim_ekle(request):
    """Personel birim ekleme endpoint'i"""
    personel_id = request.POST.get('personel_id')
    birim_id = request.POST.get('birim_id')
    gecis_tarihi = request.POST.get('gecis_tarihi')
    sorumlu = request.POST.get('sorumlu') == 'on'
    not_text = request.POST.get('not', '').strip()
    
    if not all([personel_id, birim_id, gecis_tarihi]):
        return JsonResponse({'success': False, 'message': 'Tüm zorunlu alanlar doldurulmalıdır.'})
    
    try:
        personel = Personel.objects.get(id=personel_id)
        birim = Birim.objects.get(id=birim_id)
    except (Personel.DoesNotExist, Birim.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Geçersiz personel veya birim.'})
    
    # PersonelBirim kaydı oluştur
    personel_birim = PersonelBirim.objects.create(
        personel=personel,
        birim=birim,
        gecis_tarihi=gecis_tarihi,
        sorumlu=sorumlu,
        not_text=not_text,
        created_by=request.user
    )
    
    return JsonResponse({
        'success': True, 
        'message': 'Birim ataması başarıyla kaydedildi.',
        'personel_birim': {
            'id': personel_birim.id,
            'birim_ad': personel_birim.birim.ad,
            'bina_ad': personel_birim.birim.bina.ad,
            'ust_birim_ad': personel_birim.birim.ust_birim.ad,
            'gecis_tarihi': personel_birim.gecis_tarihi.strftime('%d.%m.%Y'),
            'sorumlu': personel_birim.sorumlu
        }
    })

@login_required
def gorevlendirme_yazisi(request, personel_birim_id):
    """Görevlendirme yazısı PDF oluşturma"""
    try:
        personel_birim = get_object_or_404(PersonelBirim.objects.select_related('personel', 'birim__bina', 'birim__ust_birim', 'personel__unvan'), id=personel_birim_id)
        imza_id = request.GET.get('imza_id')
        
        if not imza_id:
            return JsonResponse({'success': False, 'message': 'İmza seçilmelidir.'})
        
        teblig_imzasi = get_object_or_404(TebligImzasi, id=imza_id)
        
        # PDF template'ini render et
        html = render_to_string('ik_core/pdf/gorevlendirme_yazisi.html', {
            'personel_birim': personel_birim,
            'teblig_imzasi': teblig_imzasi,
        })
        
        # PDF konfigürasyonu
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        options = {
            'page-size': 'A4',
            'orientation': 'Portrait',
            'margin-top': '5cm',
            'margin-right': '1.5cm',
            'margin-bottom': '1.1cm',
            'margin-left': '1.5cm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': '',
            'enable-external-links': True,
            'quiet': ''
        }
        
        pdf = pdfkit.from_string(html, False, options=options, configuration=config)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Gorevlendirme_{personel_birim.personel.ad_soyad}.pdf"
        filename = filename.replace(' ', '_')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'PDF oluşturulurken hata: {str(e)}'})
    