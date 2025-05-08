from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from ik_core.models import Personel, Unvan, Kurum  # Unvan ve Kurum eklendi
from ik_core.models.valuelists import TESKILAT_DEGERLERI  # TESKILAT_DEGERLERI eklendi
from .models import PersonelHareket, Sendika, SendikaUyelik, IcraTakibi, IcraHareketleri
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils import timezone
from django.db import models
from django.template.loader import render_to_string
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum

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
    """İcra takibi"""
    return render(request, 'mutemet_app/icra_takibi.html')

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
    personel = Personel.objects.get(personel_id=personel_id)
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

            personel = Personel.objects.get(personel_id=personel_id)

            # Hareket oluştur
            hareket = PersonelHareket.objects.create(
                personel=personel,
                hareket_tipi=hareket_tipi,
                hareket_tarihi=hareket_tarihi,
                aciklama=aciklama,
                olusturan=request.user
            )

            # Personel durumunu güncelle
            if hareket_tipi == 'AYRILMA':
                personel.durum = 'AYRILDI'
            elif hareket_tipi == 'IZIN':
                personel.durum = 'PASIF'
            elif hareket_tipi == 'DONUS':
                personel.durum = 'AKTIF'
            personel.save()

            return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def sendika_hareket_ekle(request):
    """Yeni sendika hareketi ekleme"""
    try:
        personel_id = request.POST.get('personel_id')
        hareket_tarihi = request.POST.get('hareket_tarihi')
        sendika = request.POST.get('sendika') # Formdan gelen sendika ID'si
        hareket_tipi = request.POST.get('hareket_tipi')
        aciklama = request.POST.get('aciklama', '') # Açıklama opsiyonel olabilir

        if not all([personel_id, hareket_tarihi, sendika, hareket_tipi]):
            messages.error(request, "Lütfen tüm zorunlu alanları doldurun.")
            return HttpResponseRedirect(reverse('mutemet_app:sendika_takibi'))

        # Convert hareket_tarihi to a datetime.date object
        hareket_tarihi = datetime.strptime(hareket_tarihi, '%Y-%m-%d').date()

        # Nesneleri getirelim
        personel = get_object_or_404(Personel, personel_id=personel_id)
        sendika = get_object_or_404(Sendika, sendika=sendika)

        # Nesneleri kullanarak SendikaUyelik nesnesi oluştur
        SendikaUyelik.objects.create(
            personel=personel, 
            hareket_tarihi=hareket_tarihi,
            sendika=sendika, # ForeignKey ile doğrudan sendika nesnesini atıyoruz 
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
    """List all IcraTakibi records."""
    icra_takipleri = IcraTakibi.objects.select_related('personel').all()
    return render(request, 'mutemet_app/icra_takibi.html', {'icra_takipleri': icra_takipleri})

@csrf_exempt
def icra_takibi_ekle(request):
    """Add a new IcraTakibi record."""
    if request.method == 'POST':
        try:
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

            personel = get_object_or_404(Personel, personel_id=personel_id)

            IcraTakibi.objects.create(
                personel=personel,
                icra_vergi_dairesi_no=icra_vergi_dairesi_no,
                icra_dairesi=icra_dairesi,
                dosya_no=dosya_no,
                icra_dairesi_banka=icra_dairesi_banka,
                icra_dairesi_hesap_no=icra_dairesi_hesap_no,
                alacakli=alacakli,
                alacakli_vekili=alacakli_vekili,
                tarihi=tarihi,
                tutar=tutar
            )
            messages.success(request, "İcra takibi başarıyla eklendi.")
        except Exception as e:
            messages.error(request, f"Hata: {str(e)}")
        return redirect('mutemet_app:icra_takibi_list')
    return redirect('mutemet_app:icra_takibi_list')  # Ensure a redirect for non-POST requests

@login_required
def icra_hareketleri_list(request, icra_id):
    """List all IcraHareketleri for a specific IcraTakibi."""
    icra = get_object_or_404(IcraTakibi, pk=icra_id)
    hareketler = IcraHareketleri.objects.filter(icra=icra).order_by('-kesildigi_donem')
    toplam_kesinti = hareketler.aggregate(Sum('kesilen_tutar'))['kesilen_tutar__sum'] or 0
    return render(request, 'mutemet_app/icra_hareketleri.html', {
        'icra': icra,
        'hareketler': hareketler,
        'toplam_kesinti': toplam_kesinti
    })

@csrf_exempt
def icra_hareket_ekle(request, icra_id):
    """Add a new IcraHareketleri record."""
    if request.method == 'POST':
        try:
            icra = get_object_or_404(IcraTakibi, pk=icra_id)
            kesilen_tutar = request.POST.get('kesilen_tutar')
            kesildigi_donem = request.POST.get('kesildigi_donem')
            odeme_turu = request.POST.get('odeme_turu')

            IcraHareketleri.objects.create(
                icra=icra,
                kesilen_tutar=kesilen_tutar,
                kesildigi_donem=kesildigi_donem,
                odeme_turu=odeme_turu
            )
            messages.success(request, "İcra hareketi başarıyla eklendi.")
        except Exception as e:
            messages.error(request, f"Hata: {str(e)}")
        return redirect('mutemet_app:icra_hareketleri_list', icra_id=icra_id)
