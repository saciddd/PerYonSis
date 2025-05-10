from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from ik_core.models import Personel, Unvan, Kurum  # Unvan ve Kurum eklendi
from ik_core.models.valuelists import TESKILAT_DEGERLERI  # TESKILAT_DEGERLERI eklendi
from .models import PersonelHareket, Sendika, SendikaUyelik, IcraTakibi, IcraHareketleri
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.db import models
from django.template.loader import render_to_string
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Max, Count, Q
from collections import defaultdict
import pdfkit
import locale

# Türkçe para birimi formatı için locale ayarı
locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')

def format_currency(value):
    """Sayıyı Türk Lirası formatında formatlar (10.000,00)"""
    try:
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(value)

@login_required
def index(request):
    """Mutemetlik ana sayfası"""
    return render(request, 'mutemet_app/index.html')

@login_required
def personel_takibi(request):
    """Başlayan ve ayrılan personel takibi"""
    return render(request, 'mutemet_app/personel_takibi.html')

@login_required
def sendika_takibi(request):
    """Sendika giriş-çıkış takibi"""
    sendikalar = Sendika.objects.all()
    maas_donemleri = SendikaUyelik.objects.order_by('-maas_donemi').values_list('maas_donemi', flat=True).distinct()

    # Format maaş dönemlerini "Nisan 2025" gibi göstermek için
    formatted_maas_donemleri = [
        {
            'value': donem.strftime('%Y-%m-%d'),
            'label': donem.strftime('%B %Y').capitalize()
        }
        for donem in maas_donemleri
    ]

    selected_donem = request.GET.get('maas_donemi')
    if selected_donem:
        try:
            # Parse the selected period to ensure it's in the correct format
            selected_donem = datetime.strptime(selected_donem, '%Y-%m-%d').date()
        except ValueError:
            selected_donem = None

    # select_related ve prefetch_related'ı birleştirerek kullan
    uyelikler_query = SendikaUyelik.objects.select_related('personel', 'olusturan').prefetch_related('sendika')

    if selected_donem:
        uyelikler_query = uyelikler_query.filter(maas_donemi=selected_donem)

    context = {
        'sendikalar': sendikalar,
        'uyelikler': uyelikler_query.order_by('-hareket_tarihi'),  # Sorguyu burada çalıştır
        'maas_donemleri': formatted_maas_donemleri,
        'selected_donem': selected_donem.strftime('%Y-%m-%d') if selected_donem else None
    }
    return render(request, 'mutemet_app/sendika_takibi.html', context)

@login_required
def icra_takibi(request):
    """İcra takibi ana sayfası (personel bazlı listeyi gösterir)"""
    icralar_query = IcraTakibi.objects.select_related('personel').order_by('personel__ad', 'personel__soyad', 'tarihi')

    # Tüm personellerin ID'lerini alalım (yinelenenleri önlemek için set kullanıldı)
    personel_ids = list(set(icra.personel_id for icra in icralar_query))

    # Her personel için ek bilgileri önceden hesaplayalım
    personel_ek_bilgiler_map = {}
    for p_id in personel_ids:
        aktif_icra_obj = IcraTakibi.objects.filter(personel_id=p_id, durum='AKTIF').first()
        kalan_borc_aktif = None
        if aktif_icra_obj:
            toplam_kesinti_aktif_hareketler = IcraHareketleri.objects.filter(icra=aktif_icra_obj).aggregate(Sum('kesilen_tutar'))['kesilen_tutar__sum'] or 0
            kalan_borc_aktif = float(aktif_icra_obj.tutar) - float(toplam_kesinti_aktif_hareketler)

        # En son kesinti yapılan dönemi bulmak için, o personele ait tüm icra hareketlerine bakılır
        en_son_kesinti_donemi_hareketler = IcraHareketleri.objects.filter(icra__personel_id=p_id).aggregate(Max('kesildigi_donem'))['kesildigi_donem__max']
        
        siradaki_icra_sayisi = IcraTakibi.objects.filter(personel_id=p_id, durum='SIRADA').count()

        personel_ek_bilgiler_map[p_id] = {
            'kalan_borc_aktif': kalan_borc_aktif,
            'en_son_kesinti_donemi': en_son_kesinti_donemi_hareketler,
            'siradaki_icra_sayisi': siradaki_icra_sayisi,
        }

    # Her bir icra için toplam kesinti ve kalan borcu hesaplayıp icra objesine ekleyelim
    # Bu, şablonda her icra için bu değerleri kolayca göstermemizi sağlar
    processed_icralar = []
    for icra_obj in icralar_query:
        toplam_kesinti = IcraHareketleri.objects.filter(icra=icra_obj).aggregate(Sum('kesilen_tutar'))['kesilen_tutar__sum'] or 0
        icra_obj.hesaplanan_toplam_kesinti = toplam_kesinti
        icra_obj.hesaplanan_kalan_borc = float(icra_obj.tutar) - float(toplam_kesinti)
        processed_icralar.append(icra_obj)

    personel_icra_data = defaultdict(lambda: {'icralar': [], 'ek_bilgiler': {}})
    for icra_obj in processed_icralar: 
        personel_icra_data[icra_obj.personel]['icralar'].append(icra_obj)
        # Ek bilgileri, her personel için sadece bir kez atayalım
        if not personel_icra_data[icra_obj.personel]['ek_bilgiler']:
             personel_icra_data[icra_obj.personel]['ek_bilgiler'] = personel_ek_bilgiler_map.get(icra_obj.personel.id, {})
             
    # Dönem seçenekleri (6 ay önce - 6 ay sonrası)
    today = date.today().replace(day=1)
    donem_secenekleri = [(today + relativedelta(months=delta)) for delta in range(-6, 7)]

    return render(request, 'mutemet_app/icra_takibi.html', {
        'personel_icra_data': dict(personel_icra_data), # defaultdict'u şablona göndermeden önce dict'e çevir
        'donem_secenekleri': donem_secenekleri,
    })

@login_required
def odeme_takibi(request):
    """Ödeme takibi"""
    return render(request, 'mutemet_app/odeme_takibi.html')

@login_required
def personel_listesi(request):
    """Personel listesi görüntüleme ve arama"""
    personeller = Personel.objects.all()
    tc_kimlik_no = request.GET.get('tc_kimlik_no', '').strip()
    ad_soyad = request.GET.get('ad_soyad', '').strip()
    unvanlar = request.GET.getlist('unvan')
    kurumlar = request.GET.getlist('kurum')
    teskilatlar = request.GET.getlist('teskilat')

    if tc_kimlik_no:
        personeller = personeller.filter(tc_kimlik_no__icontains=tc_kimlik_no)
    if ad_soyad:
        personeller = personeller.filter(
            models.Q(ad__icontains=ad_soyad) | models.Q(soyad__icontains=ad_soyad)
        )
    if unvanlar:
        personeller = personeller.filter(unvan_id__in=unvanlar)
    if kurumlar:
        personeller = personeller.filter(kurum_id__in=kurumlar)
    if teskilatlar:
        personeller = personeller.filter(teskilat__in=teskilatlar)

    unvan_list = Unvan.objects.all()
    kurum_list = Kurum.objects.all()

    context = {
        'personeller': personeller,
        'unvan_list': unvan_list,
        'kurum_list': kurum_list,
        'teskilat_choices': TESKILAT_DEGERLERI,
        'filter_tc_kimlik_no': tc_kimlik_no,
        'filter_ad_soyad': ad_soyad,
        'filter_unvanlar': [int(u) for u in unvanlar],
        'filter_kurumlar': [int(k) for k in kurumlar],
        'filter_teskilatlar': teskilatlar,
    }
    return render(request, 'mutemet_app/personeller.html', context)

@login_required
def hareket_listesi(request):
    """Personel hareket listesi"""
    personel_id = request.GET.get('personel_id')
    # Yeni modele göre tc_kimlik_no ile bul
    personel = get_object_or_404(Personel, tc_kimlik_no=personel_id)
    hareketler = PersonelHareket.objects.filter(personel=personel).order_by('-hareket_tarihi').select_related('olusturan')
    return render(request, 'mutemet_app/hareket_listesi.html', {
        'personel': personel,
        'hareketler': hareketler
    })

@login_required
@require_http_methods(["POST"])
def hareket_ekle(request):
    """Yeni hareket ekleme"""
    try:
        with transaction.atomic():
            personel_id = request.POST.get('personel_id')
            hareket_tipi = request.POST.get('hareket_tipi')
            hareket_tarihi = request.POST.get('hareket_tarihi')
            aciklama = request.POST.get('aciklama')

            personel = get_object_or_404(Personel, tc_kimlik_no=personel_id)

            hareket = PersonelHareket.objects.create(
                personel=personel,
                hareket_tipi=hareket_tipi,
                hareket_tarihi=hareket_tarihi,
                aciklama=aciklama,
                olusturan=request.user
            )

            return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def sendika_hareket_ekle(request):
    """Yeni sendika hareketi ekleme"""
    try:
        personel_id = request.POST.get('personel_id')  # DÜZELTİLDİ
        hareket_tarihi = request.POST.get('hareket_tarihi')
        sendika = request.POST.get('sendika')
        hareket_tipi = request.POST.get('hareket_tipi')
        aciklama = request.POST.get('aciklama', '')

        if not all([personel_id, hareket_tarihi, sendika, hareket_tipi]):
            messages.error(request, f"Lütfen tüm zorunlu alanları doldurun.{personel_id} {hareket_tarihi} {sendika} {hareket_tipi}")
            return HttpResponseRedirect(reverse('mutemet_app:sendika_takibi'))

        hareket_tarihi = datetime.strptime(hareket_tarihi, '%Y-%m-%d').date()

        # Personel'i tc_kimlik_no ile bul
        personel = get_object_or_404(Personel, tc_kimlik_no=personel_id)
        sendika = get_object_or_404(Sendika, sendika_id=sendika)

        SendikaUyelik.objects.create(
            personel=personel,
            hareket_tarihi=hareket_tarihi,
            sendika=sendika,
            hareket_tipi=hareket_tipi,
            aciklama=aciklama,
            olusturan=request.user
        )
        messages.success(request, "Sendika hareketi başarıyla eklendi.")

    except ObjectDoesNotExist:
        messages.error(request, "Seçilen personel veya sendika bulunamadı.")
    except ValidationError as e:
        messages.error(request, f"Bir hata oluştu: {e}")
    except Exception as e:
        messages.error(request, f"Beklenmedik bir hata oluştu: {e}")

    return HttpResponseRedirect(reverse('mutemet_app:sendika_takibi'))

@login_required
@require_POST
def sendika_hareket_sil(request, pk):
    """Sendika üyelik hareketini siler (AJAX)"""
    try:
        uyelik = get_object_or_404(SendikaUyelik, pk=pk)
        uyelik.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_GET
def personel_ara(request):
    """TC Kimlik No veya Ad/Soyad ile personel arama (AJAX)"""
    query = request.GET.get('q', '')
    personeller = Personel.objects.filter(
        models.Q(tc_kimlik_no__icontains=query) |
        models.Q(ad__icontains=query) |
        models.Q(soyad__icontains=query)
    ).all()[:10]  # İlk 10 sonucu al

    results = [
        {
            'id': p.tc_kimlik_no,
            'text': f"{p.tc_kimlik_no} - {p.ad} {p.soyad}",
            'ad_soyad': f"{p.ad} {p.soyad}",
            'unvan': p.unvan.ad if p.unvan else ""
        }
        for p in personeller
    ]
    return JsonResponse({'results': results})

@login_required
@require_GET
def get_sendika_modal_content(request):
    """Sendika yönetimi modal içeriğini döndürür (AJAX)"""
    sendikalar = Sendika.objects.all().order_by('sendika_adi')
    html = render_to_string('mutemet_app/_sendika_modal_content.html', {'sendikalar': sendikalar}, request=request)
    return JsonResponse({'html': html})

@login_required
@require_POST
def sendika_ekle(request):
    """Yeni sendika ekler (AJAX)"""
    sendika_adi = request.POST.get('sendika_adi', '').strip()
    if not sendika_adi:
        return JsonResponse({'success': False, 'message': 'Sendika adı boş olamaz.'})
    
    if Sendika.objects.filter(sendika_adi=sendika_adi).exists():
        return JsonResponse({'success': False, 'message': 'Bu isimde bir sendika zaten mevcut.'})
    
    try:
        sendika = Sendika.objects.create(sendika_adi=sendika_adi, olusturan=request.user)
        return JsonResponse({
            'success': True, 
            'sendika': {
                'id': sendika.sendika_id,
                'ad': sendika.sendika_adi
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Sendika eklenirken hata: {e}'})

@login_required
@require_POST
def sendika_guncelle(request, pk):
    """Sendika adını günceller (AJAX)"""
    yeni_ad = request.POST.get('sendika_adi', '').strip()
    if not yeni_ad:
        return JsonResponse({'success': False, 'message': 'Sendika adı boş olamaz.'})
        
    try:
        sendika = get_object_or_404(Sendika, pk=pk)
        # Yeni isim başka bir sendikaya ait mi kontrol et
        if Sendika.objects.filter(sendika_adi=yeni_ad).exclude(pk=pk).exists():
             return JsonResponse({'success': False, 'message': 'Bu isimde başka bir sendika zaten mevcut.'})
             
        sendika.sendika_adi = yeni_ad
        sendika.guncelleyen = request.user
        sendika.save()
        return JsonResponse({'success': True})
    except ObjectDoesNotExist:
         return JsonResponse({'success': False, 'message': 'Sendika bulunamadı.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Sendika güncellenirken hata: {e}'})

@login_required
@require_POST
def sendika_sil(request, pk):
    """Sendikayı siler (AJAX)"""
    try:
        sendika = get_object_or_404(Sendika, pk=pk)
        # İlişkili SendikaUyelik kaydı var mı kontrol et
        if SendikaUyelik.objects.filter(sendika=sendika).exists():
            return JsonResponse({'success': False, 'message': 'Bu sendikaya ait üyelik kayıtları olduğu için silinemez.'})
            
        sendika.delete()
        return JsonResponse({'success': True})
    except ObjectDoesNotExist:
         return JsonResponse({'success': False, 'message': 'Sendika bulunamadı.'})
    except Exception as e:
        # İlişkili kayıtlar nedeniyle silme hatası (IntegrityError) gibi durumlar
        return JsonResponse({'success': False, 'message': f'Sendika silinirken bir hata oluştu. Muhtemelen ilişkili kayıtlar mevcut: {e}'})

@login_required
@require_GET
def get_sendikalar_json(request):
    """Sendika listesini JSON formatında döndürür (AJAX)"""
    sendikalar = Sendika.objects.all().order_by('sendika_adi')
    data = [{'id': s.sendika_id, 'text': s.sendika_adi} for s in sendikalar]
    return JsonResponse({'results': data})

@login_required
def icra_takibi_list(request):
    """Personel bazlı ağaç yapısında icra kayıtlarını listeler."""
    print("ICRA TAKIBI LISTEYE GİRDİ")
    icralar = IcraTakibi.objects.select_related('personel').order_by('personel__ad', 'tarihi')
    personel_icra = defaultdict(list)
    for icra in icralar:
        # DEBUG: Her icra kaydını ve ilişkili personeli konsola yaz
        print(f"ICRA: {icra.id} - {icra.personel.tc_kimlik_no} - {icra.personel.ad_soyad} - {icra.durum} - {icra.tutar}")
        personel_icra[icra.personel].append(icra)
    print("PERSONEL_ICRA anahtarları (Personel):", [f"{p.tc_kimlik_no} - {p.ad_soyad}" for p in personel_icra.keys()])
    print("Her personelin icra sayısı:", {f"{p.tc_kimlik_no}": len(icralar) for p, icralar in personel_icra.items()})
    return render(request, 'mutemet_app/icra_takibi.html', {
        'personel_icra': personel_icra,
    })

@csrf_exempt
def icra_takibi_ekle(request):
    """Add a new IcraTakibi record. Önceki icra kapanmadan yeni icra eklenebilir, ancak durumu SIRADA olur."""
    if request.method == 'POST':
        try:
            # DEBUG: Gelen POST verilerini konsola yaz
            print("ICRA TAKIBI EKLE POST DATA:", dict(request.POST))

            personel_id = request.POST.get('personel_id')
            icra_vergi_dairesi_no = request.POST.get('icra_vergi_dairesi_no')
            icra_dairesi = request.POST.get('icra_dairesi')
            dosya_no = request.POST.get('dosya_no')
            icra_dairesi_banka = request.POST.get('icra_dairesi_banka')
            icra_dairesi_hesap_no = request.POST.get('icra_dairesi_hesap_no')
            alacakli = request.POST.get('alacakli')
            alacakli_vekili = request.POST.get('alacakli_vekili')
            tarihi = request.POST.get('tarihi')
            tutar = request.POST.get('tutar')

            # DEBUG: Her bir alanı ayrı ayrı yazdır
            print("personel_id:", personel_id)
            print("icra_vergi_dairesi_no:", icra_vergi_dairesi_no)
            print("icra_dairesi:", icra_dairesi)
            print("dosya_no:", dosya_no)
            print("icra_dairesi_banka:", icra_dairesi_banka)
            print("icra_dairesi_hesap_no:", icra_dairesi_hesap_no)
            print("alacakli:", alacakli)
            print("alacakli_vekili:", alacakli_vekili)
            print("tarihi:", tarihi)
            print("tutar:", tutar)

            if not (personel_id and icra_dairesi and dosya_no and tutar and tarihi):
                print("Eksik alanlar var!")
                messages.error(request, "Zorunlu alanlar eksik.")
                return redirect('mutemet_app:icra_takibi_list')

            try:
                personel = Personel.objects.get(tc_kimlik_no=personel_id)
            except Personel.DoesNotExist:
                print("Personel bulunamadı:", personel_id)
                messages.error(request, "Personel bulunamadı.")
                return redirect('mutemet_app:icra_takibi_list')

            try:
                tutar_decimal = float(tutar)
            except Exception:
                print("Tutar sayısal değil:", tutar)
                messages.error(request, "Tutar sayısal olmalı.")
                return redirect('mutemet_app:icra_takibi_list')

            try:
                tarih_obj = datetime.strptime(tarihi, "%Y-%m-%d").date()
            except Exception:
                print("Tarih formatı hatalı:", tarihi)
                messages.error(request, "Tarih formatı hatalı.")
                return redirect('mutemet_app:icra_takibi_list')

            # Önceki icra kapanmadan yeni icra eklenebilir, ancak durumu SIRADA olmalı
            onceki_icra = IcraTakibi.objects.filter(
                personel=personel
            ).exclude(durum='KAPANDI').order_by('-tarihi').first()
            if onceki_icra and onceki_icra.durum in ['AKTIF', 'SIRADA']:
                durum = 'SIRADA'
            else:
                durum = 'AKTIF'

            icra = IcraTakibi.objects.create(
                personel=personel,
                icra_vergi_dairesi_no=icra_vergi_dairesi_no or "",
                icra_dairesi=icra_dairesi,
                dosya_no=dosya_no,
                icra_dairesi_banka=icra_dairesi_banka or "",
                icra_dairesi_hesap_no=icra_dairesi_hesap_no or "",
                alacakli=alacakli or "",
                alacakli_vekili=alacakli_vekili or "",
                tarihi=tarih_obj,
                tutar=tutar_decimal,
                durum=durum
            )
            print("İcra kaydı başarıyla eklendi:", icra)
            messages.success(request, "İcra takibi başarıyla eklendi.")
        except Exception as e:
            import traceback
            print("İcra ekleme hatası:", str(e))
            print(traceback.format_exc())
            messages.error(request, f"Hata: {str(e)}\n{traceback.format_exc()}")
        return redirect('mutemet_app:icra_takibi_list')
    return redirect('mutemet_app:icra_takibi_list')

@login_required
def icra_hareketleri_list(request, icra_id):
    """İcra hareketleri modal içeriği (partial)"""
    icra = get_object_or_404(IcraTakibi, pk=icra_id)
    hareketler = IcraHareketleri.objects.filter(icra=icra).order_by('-kesildigi_donem')
    toplam_kesinti = hareketler.aggregate(Sum('kesilen_tutar'))['kesilen_tutar__sum'] or 0
    kalan_borc = float(icra.tutar) - float(toplam_kesinti)
    today = date.today().replace(day=1)
    donem_secenekleri = [(today + relativedelta(months=delta)) for delta in range(-6, 7)]
    return render(request, 'mutemet_app/_icra_hareket_modal_content.html', {
        'icra': icra,
        'hareketler': hareketler,
        'toplam_kesinti': toplam_kesinti,
        'kalan_borc': kalan_borc,
        'donem_secenekleri': donem_secenekleri,
    })

@csrf_exempt
def icra_hareket_ekle(request, icra_id):
    """AJAX: Yeni icra hareketi ekle, kalan borç kontrolü ile"""
    icra = get_object_or_404(IcraTakibi, pk=icra_id)
    if request.method == 'POST':
        try:
            kesilen_tutar = request.POST.get('kesilen_tutar')
            kesildigi_donem = request.POST.get('kesildigi_donem')
            odeme_turu = request.POST.get('odeme_turu')

            toplam_kesinti = IcraHareketleri.objects.filter(icra=icra).aggregate(Sum('kesilen_tutar'))['kesilen_tutar__sum'] or 0
            kalan_borc = float(icra.tutar) - float(toplam_kesinti)
            if float(kesilen_tutar) > kalan_borc:
                return JsonResponse({'success': False, 'message': 'Kesilen tutar kalan borçtan fazla olamaz!'})

            IcraHareketleri.objects.create(
                icra=icra,
                kesilen_tutar=kesilen_tutar,
                kesildigi_donem=kesildigi_donem,
                odeme_turu=odeme_turu
            )
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Geçersiz istek.'})

@login_required
def icra_modal_view(request, icra_id):
    """İcra hareketleri modalı için dönem seçenekleri ve icra bilgisi"""
    icra = get_object_or_404(IcraTakibi, pk=icra_id)
    today = date.today()
    donem_secenekleri = [
        (today + relativedelta(months=delta)).replace(day=1)
        for delta in range(-6, 7)
    ]
    secili_donem = request.GET.get('kesildigi_donem', today.replace(day=1).isoformat())
    return render(request, 'mutemet_app/icra_modal.html', {
        'icra': icra,
        'donem_secenekleri': donem_secenekleri,
        'secili_donem': secili_donem,
    })

@login_required
def aylik_icra_kesinti(request):
    """Seçilen döneme ait icra kesintilerini PDF olarak raporlar"""
    try:
        # Dönem parametresini al
        donem = request.GET.get('donem')
        if not donem:
            messages.error(request, "Dönem seçilmedi.")
            return redirect('mutemet_app:icra_takibi')

        # Dönem tarihini parse et
        donem_tarihi = datetime.strptime(donem, '%Y-%m-%d').date()
        
        # Seçilen döneme ait icra hareketlerini al
        hareketler = IcraHareketleri.objects.filter(
            kesildigi_donem=donem_tarihi
        ).select_related('icra', 'icra__personel').order_by('icra__personel__ad', 'icra__personel__soyad')

        if not hareketler.exists():
            messages.error(request, "Seçilen döneme ait icra kesintisi bulunamadı.")
            return redirect('mutemet_app:icra_takibi')

        # Toplam kesinti tutarını hesapla
        toplam_kesinti = hareketler.aggregate(Sum('kesilen_tutar'))['kesilen_tutar__sum'] or 0

        # Türkçe ay ve yıl bilgilerini hazırla
        ay_adi = donem_tarihi.strftime('%B').upper()
        yil = donem_tarihi.year

        # Her bir hareket için kesilen tutarı formatla
        for hareket in hareketler:
            hareket.formatted_kesilen_tutar = format_currency(hareket.kesilen_tutar)

        # Template context
        context = {
            'hareketler': hareketler,
            'toplam_kesinti': format_currency(toplam_kesinti),
            'donem_ay': ay_adi,
            'donem_yil': yil
        }

        # HTML template'i render et
        html_string = render_to_string('mutemet_app/aylik_icra_kesinti.html', context)

        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

        # PDF oluştur
        pdf = pdfkit.from_string(html_string, False, options={
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'margin-top': '1cm',
            'margin-right': '1cm',
            'margin-bottom': '1cm',
            'margin-left': '1cm',
        }, configuration=config)

        # PDF'i response olarak döndür
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="icra_kesinti_{donem_tarihi.strftime("%Y_%m")}.pdf"'
        return response

    except Exception as e:
        messages.error(request, f"PDF oluşturulurken bir hata oluştu: {str(e)}")
        return redirect('mutemet_app:icra_takibi')