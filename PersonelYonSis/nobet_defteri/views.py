from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponseForbidden, JsonResponse
from .forms import NobetDefteriForm, NobetOlayKaydiForm, KontrolFormuForm, KontrolCevapFormSet, DinamikKontrolForm, KontrolSoruForm, NobetciTeknikerForm
from .models import NobetDefteri, NobetTuru, NobetOlayKaydi, KontrolSoru, KontrolFormu, KontrolCevap, NobetciTekniker
from PersonelYonSis.views import get_user_permissions
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.http import HttpResponse
import pdfkit
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from pathlib import Path
from django.db.models import F, ExpressionWrapper, DurationField, Sum
from datetime import datetime, timedelta, time
from collections import defaultdict
User = get_user_model()

# Nöbet defteri listesi
def nobet_defteri_list(request):
    defterler = NobetDefteri.objects.all().order_by('-tarih', '-created_at')
    onay_yetkisi = 'Nöbet Defteri Onaylayabilir' in get_user_permissions(request.user)
    # Her defter için önemli olay sayısını ekle
    defterler_with_onemli = []
    for defter in defterler:
        onemli_sayi = defter.olaylar.filter(onemli=True).count()
        defterler_with_onemli.append({
            'defter': defter,
            'onemli_sayi': onemli_sayi
        })
    return render(request, 'nobet_defteri/list.html', {'defterler_with_onemli': defterler_with_onemli, 'onay_yetkisi': onay_yetkisi})

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
    # Tekniker kayıtları
    teknikerler = defter.teknikerler.order_by('gelis_saati')

    # Determine if current user is the creator
    is_creator = (hasattr(defter, 'olusturan') and defter.olusturan == request.user)

    # --- Olay ekleme işlemi ---
    if request.method == 'POST' and 'olay_ekle' in request.POST:
        # Only the creator may add events
        if not is_creator:
            return HttpResponseForbidden("Sadece defteri oluşturan kullanıcı olay ekleyebilir.")
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
        # If not the creator, render the event form as readonly
        if not is_creator:
            for f in form.fields.values():
                f.required = False
                f.widget.attrs['disabled'] = 'disabled'

    # --- Nobetçi Tekniker ekleme işlemi ---
    tekniker_form = NobetciTeknikerForm()
    teknikerler = defter.teknikerler.order_by('gelis_saati')
    tekniker_hata = None
    if request.method == 'POST' and 'tekniker_ekle' in request.POST:
        if not is_creator:
            return HttpResponseForbidden("Sadece defteri oluşturan kullanıcı tekniker ekleyebilir.")
        tekniker_form = NobetciTeknikerForm(request.POST)
        if tekniker_form.is_valid():
            tekniker_adi = tekniker_form.cleaned_data['tekniker_adi']
            if defter.teknikerler.filter(tekniker_adi=tekniker_adi).exists():
                tekniker_hata = "Bu tekniker adı zaten kayıtlı."
            else:
                tekniker = tekniker_form.save(commit=False)
                tekniker.defter = defter
                tekniker.save()
                messages.success(request, "Tekniker kaydı eklendi.")
                return redirect('nobet_defteri:detay', defter.id)
    else:
        # If not the creator, render the tekniker form as readonly
        if not is_creator:
            for f in tekniker_form.fields.values():
                f.required = False
                f.widget.attrs['disabled'] = 'disabled'

    # --- Kontrol formu verileri ---
    aktif_sorular = KontrolSoru.objects.filter(aktif=True)
    kontrol_formu, created = KontrolFormu.objects.get_or_create(nobet_defteri=defter)

    # If POST to save kontrol form, ensure only creator and not-onayli can save
    if request.method == 'POST' and 'kontrol_formu_kaydet' in request.POST:
        if not is_creator or defter.onayli:
            messages.warning(request, "Kontrol formunu yalnızca defteri oluşturan kullanıcı düzenleyebilir veya defter onaylıysa düzenlenemez.")
            return redirect('nobet_defteri:detay', defter.id)
            # --- IGNORE ---
        # Bound form ile POST verisini işle
        kontrol_form = DinamikKontrolForm(request.POST, sorular=aktif_sorular)
        if kontrol_form.is_valid():
            for soru in aktif_sorular:
                cevap_raw = kontrol_form.cleaned_data.get(f"soru_{soru.id}_cevap")
                aciklama = kontrol_form.cleaned_data.get(f"soru_{soru.id}_aciklama")
                # normalize: boş string veya None -> None, 'True' -> True, 'False' -> False
                if isinstance(cevap_raw, str):
                    cr = cevap_raw.strip()
                    if cr == '':
                        cevap = None
                    elif cr.lower() in ('true', '1', 't', 'y', 'yes', 'e'):
                        cevap = True
                    else:
                        cevap = False
                else:
                    cevap = bool(cevap_raw) if cevap_raw is not None else None
                KontrolCevap.objects.update_or_create(
                    form=kontrol_formu,
                    soru=soru,
                    defaults={'cevap': cevap, 'aciklama': aciklama}
                )
            messages.success(request, "Kontrol formu kaydedildi.")
            return redirect('nobet_defteri:detay', defter.id)
        # eğer geçersizse bound kontrol_form ile devam edecek (hataları göster)
    else:
        # GET: mevcut cevapları initial olarak yükle
        initial = {}
        mevcut_cevaplar = KontrolCevap.objects.filter(form=kontrol_formu).select_related('soru')
        for cvp in mevcut_cevaplar:
            key_cevap = f"soru_{cvp.soru.id}_cevap"
            key_aciklama = f"soru_{cvp.soru.id}_aciklama"
            # cvp.cevap None ise initial bırak ('' => hiçbir radio seçili olmaz)
            if cvp.cevap is True:
                initial[key_cevap] = 'True'
            elif cvp.cevap is False:
                initial[key_cevap] = 'False'
            else:
                initial[key_cevap] = ''
            initial[key_aciklama] = cvp.aciklama or ''
        kontrol_form = DinamikKontrolForm(initial=initial, sorular=aktif_sorular)

        # If current user is not the creator OR the defter is approved, make kontrol form readonly
        if (not is_creator) or defter.onayli:
            for f in kontrol_form.fields.values():
                f.required = False
                f.widget.attrs['disabled'] = 'disabled'

    # Yeni: kontrol_items oluştur (her biri: {'soru': soru, 'cevap_field': BoundField, 'aciklama_field': BoundField})
    kontrol_items = []
    for soru in aktif_sorular:
        cevap_name = f"soru_{soru.id}_cevap"
        aciklama_name = f"soru_{soru.id}_aciklama"
        # BoundField elde etmek için form[...] kullanıyoruz; yoksa None olabilir
        cevap_field = kontrol_form[cevap_name] if cevap_name in kontrol_form.fields else None
        aciklama_field = kontrol_form[aciklama_name] if aciklama_name in kontrol_form.fields else None
        kontrol_items.append({
            'soru': soru,
            'cevap_field': cevap_field,
            'aciklama_field': aciklama_field,
        })

    return render(request, 'nobet_defteri/detay.html', {
        'defter': defter,
        'olaylar': olaylar,
        'form': form,
        'kontrol_form': kontrol_form,
        'aktif_sorular': aktif_sorular,
        'kontrol_items': kontrol_items,
        'is_defter_creator': is_creator,
        'tekniker_form': tekniker_form,
        'teknikerler': teknikerler,
        'tekniker_hata': tekniker_hata,
    })

# Tekniker kaydı silme
from django.views.decorators.http import require_POST

@require_POST
def nobetci_tekniker_sil(request, defter_id, tekniker_id):
    defter = get_object_or_404(NobetDefteri, id=defter_id)
    tekniker = get_object_or_404(NobetciTekniker, id=tekniker_id, defter=defter)
    if not (hasattr(defter, 'olusturan') and defter.olusturan == request.user):
        return HttpResponseForbidden("Sadece defteri oluşturan kullanıcı silebilir.")
    tekniker.delete()
    messages.success(request, "Tekniker kaydı silindi.")
    return redirect('nobet_defteri:detay', defter.id)

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

def nobet_defteri_pdf(request, defter_id):
    defter = get_object_or_404(NobetDefteri, id=defter_id)
    # Giriş yapan kullanıcı bilgisini PDF'e ekle
    loginuser = request.user if request.user.is_authenticated else None
    olaylar = defter.olaylar.order_by('saat')
    # Yeni: kontrol formu ve cevaplarını al
    kontrol_formu = KontrolFormu.objects.filter(nobet_defteri=defter).first()
    kontrol_cevaplar = KontrolCevap.objects.filter(form=kontrol_formu).select_related('soru') if kontrol_formu else []
    now = timezone.now()

    # Build an absolute file:// path to the logo if STATIC_ROOT is set
    pdf_logo = None
    try:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root:
            logo_path = Path(static_root) / 'logo' / 'kdh_logo.png'
            if logo_path.exists():
                pdf_logo = f"file://{logo_path.as_posix()}"
    except Exception:
        pdf_logo = None

    html = render_to_string('nobet_defteri/defter_pdf.html', {
        'defter': defter,
        'olaylar': olaylar,
        'kontrol_cevaplar': kontrol_cevaplar,
        'now': now,
        'user': loginuser,
        'pdf_logo': pdf_logo,
    })
    options = {
        'page-size': 'A4',
        'orientation': 'Portrait',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': True,
        'enable-external-links': True,
        'quiet': ''
    }
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="nobet_defteri_{defter.id}.pdf"'
    return response

@csrf_exempt
def nobet_defteri_pdf_modal(request, defter_id):
    defter = get_object_or_404(NobetDefteri, id=defter_id)
    if request.method == 'POST' and not defter.onayli:
        yeni_aciklama = request.POST.get('aciklama', '').strip()
        if yeni_aciklama != defter.aciklama:
            defter.aciklama = yeni_aciklama
            defter.save()
    olaylar = defter.olaylar.order_by('saat')
    # Yeni: kontrol formu ve cevaplarını al (modal için de)
    kontrol_formu = KontrolFormu.objects.filter(nobet_defteri=defter).first()
    kontrol_cevaplar = KontrolCevap.objects.filter(form=kontrol_formu).select_related('soru') if kontrol_formu else []
    now = timezone.now()
    loginuser = request.user if request.user.is_authenticated else None

    # Build pdf_logo as above
    pdf_logo = None
    try:
        static_root = getattr(settings, 'STATIC_ROOT', None)
        if static_root:
            logo_path = Path(static_root) / 'logo' / 'kdh_logo.png'
            if logo_path.exists():
                pdf_logo = f"file://{logo_path.as_posix()}"
    except Exception:
        pdf_logo = None

    html = render_to_string('nobet_defteri/defter_pdf.html', {
        'defter': defter,
        'olaylar': olaylar,
        'kontrol_cevaplar': kontrol_cevaplar,
        'now': now,
        'user': loginuser,
        'pdf_logo': pdf_logo,
    })
    options = {
        'page-size': 'A4',
        'orientation': 'Portrait',
        'margin-top': '1.5cm',
        'margin-right': '1.5cm',
        'margin-bottom': '1.1cm',
        'margin-left': '1.5cm',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': True,
        'enable-external-links': True,
        'quiet': ''
    }
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="nobet_defteri_{defter.id}.pdf"'
    return response

# KontrolSoru CRUD (liste/ekle/guncelle/sil)
def kontrol_soru_list(request):
    if not request.user.has_permission('Kontrol Soru Yönetebilir'):
        return HttpResponseForbidden("Yetkiniz yok.")
    sorular = KontrolSoru.objects.all().order_by('id')
    return render(request, 'nobet_defteri/kontrol_soru_list.html', {'sorular': sorular})

def kontrol_soru_ekle(request):
    if not request.user.has_permission('Kontrol Soru Yönetebilir'):
        return HttpResponseForbidden("Yetkiniz yok.")
    if request.method == 'POST':
        form = KontrolSoruForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Soru eklendi.")
            return redirect('nobet_defteri:kontrol_soru_list')
    else:
        form = KontrolSoruForm()
    return render(request, 'nobet_defteri/kontrol_soru_form.html', {'form': form, 'is_update': False})

def kontrol_soru_guncelle(request, pk):
    if not request.user.has_permission('Kontrol Soru Yönetebilir'):
        return HttpResponseForbidden("Yetkiniz yok.")
    soru = get_object_or_404(KontrolSoru, pk=pk)
    if request.method == 'POST':
        form = KontrolSoruForm(request.POST, instance=soru)
        if form.is_valid():
            form.save()
            messages.success(request, "Soru güncellendi.")
            return redirect('nobet_defteri:kontrol_soru_list')
    else:
        form = KontrolSoruForm(instance=soru)
    return render(request, 'nobet_defteri/kontrol_soru_form.html', {'form': form, 'is_update': True, 'soru': soru})

def kontrol_soru_sil(request, pk):
    if not request.user.has_permission('Kontrol Soru Yönetebilir'):
        return HttpResponseForbidden("Yetkiniz yok.")
    soru = get_object_or_404(KontrolSoru, pk=pk)
    if request.method == 'POST':
        soru.delete()
        messages.success(request, "Soru silindi.")
        return redirect('nobet_defteri:kontrol_soru_list')
    # GET için onay sayfası yerine hızlı redirect (veya isterseniz onay template ekleyin)
    return redirect('nobet_defteri:kontrol_soru_list')

def tekniker_ziyaretleri(request):
    # Tarih aralığı al
    baslangic = request.GET.get('baslangic')
    bitis = request.GET.get('bitis')
    tekniker_adi_arama = request.GET.get('tekniker_adi', '').strip()
    ziyaretler = []
    gruplar = defaultdict(list)
    toplam_sureler = {}

    # Tarih parse
    try:
        baslangic_dt = datetime.strptime(baslangic, '%Y-%m-%d').date() if baslangic else None
        bitis_dt = datetime.strptime(bitis, '%Y-%m-%d').date() if bitis else None
    except Exception:
        baslangic_dt = bitis_dt = None

    qs = NobetciTekniker.objects.select_related('defter')
    if baslangic_dt:
        qs = qs.filter(defter__tarih__gte=baslangic_dt)
    if bitis_dt:
        qs = qs.filter(defter__tarih__lte=bitis_dt)
    if tekniker_adi_arama:
        qs = qs.filter(tekniker_adi__icontains=tekniker_adi_arama)

    qs = qs.order_by('tekniker_adi', 'defter__tarih', 'gelis_saati')

    # Gruplama ve süre hesaplama
    for z in qs:
        # Süre hesaplama
        gs = z.gelis_saati
        as_ = z.ayrilis_saati
        # datetime objesine çevir
        gs_dt = datetime.combine(z.defter.tarih, gs)
        as_dt = datetime.combine(z.defter.tarih, as_)
        if as_ < gs:
            as_dt += timedelta(days=1)
        sure = as_dt - gs_dt
        # Süreyi string olarak hazırla
        total_seconds = int(sure.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        sure_str = f"{hours} saat {minutes} dk"
        gruplar[z.tekniker_adi].append({
            'gun': z.defter.tarih,
            'gelis_saati': gs,
            'ayrilis_saati': as_,
            'sure': sure,
            'sure_str': sure_str,
        })
        toplam_sureler.setdefault(z.tekniker_adi, timedelta())
        toplam_sureler[z.tekniker_adi] += sure

    # Listeyi kolay işlemek için dönüştür
    ziyaretler = [
        {
            'tekniker_adi': adi,
            'kayitlar': kayitlar,
            'toplam_sure': toplam_sureler[adi],
        }
        for adi, kayitlar in gruplar.items()
    ]

    # Toplam saat string olarak gösterilecek
    for z in ziyaretler:
        td = z['toplam_sure']
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        z['toplam_sure_str'] = f"{hours} saat {minutes} dk"

    context = {
        'ziyaretler': ziyaretler,
        'baslangic': baslangic,
        'bitis': bitis,
        'tekniker_adi_arama': tekniker_adi_arama,
    }
    return render(request, 'nobet_defteri/tekniker_ziyaretleri.html', context)
