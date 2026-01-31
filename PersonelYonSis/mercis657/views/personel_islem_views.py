from tkinter import Y
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import datetime, date
import json

from mercis657.views.main_views import yarim_zamanli_calisma_kaydet
from ..models import Personel, PersonelListesi, PersonelListesiKayit, Mesai, Mesai_Tanimlari, ResmiTatil, MazeretKaydi, SabitMesai, YarimZamanliCalisma, UserMesaiFavori
from ..utils import hesapla_fazla_mesai, get_favori_mesailer


@login_required
@require_POST
def hazir_mesai_ata(request, personel_id, liste_id, year, month):
    """Seçilen günlere hazır mesai atar"""
    if not request.user.has_permission('ÇS 657 Çizelge Sayfası'):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        mesai_tanim_id = data.get('mesai_tanim_id')
        gunler = data.get('gunler', [])  # [1, 5, 10] gibi gün numaraları
        
        if not mesai_tanim_id or not gunler:
            return JsonResponse({'status': 'error', 'message': 'Mesai tanımı ve günler seçilmelidir.'})
        
        personel = get_object_or_404(Personel, pk=personel_id)
        mesai_tanim = get_object_or_404(Mesai_Tanimlari, pk=mesai_tanim_id)
                
        created_count = 0
        
        for gun_no in gunler:
            current_date = date(year, month, gun_no)
            
            # Bu güne zaten mesai var mı kontrol et
            existing = Mesai.objects.filter(
                Personel=personel,
                MesaiDate=current_date
            ).first()
            
            if not existing:
                Mesai.objects.create(
                    Personel=personel,
                    MesaiDate=current_date,
                    MesaiTanim=mesai_tanim,
                    OnayDurumu=True,
                    Degisiklik=False
                )
                created_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'{created_count} güne mesai atandı.',
            'created_count': created_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def personel_profil(request, personel_id, liste_id, year, month):
    """Personel profil modalını döner"""
    personel = get_object_or_404(Personel, pk=personel_id)
    liste = get_object_or_404(PersonelListesi, pk=liste_id)
    user = request.user
    # Tüm Sabit mesaileri çekiyoruz - güvenli şekilde
    try:
        # Problemli ara_dinlenme değerlerini filtrele
        sabit_mesailer = []
        for sm in SabitMesai.objects.all():
            try:
                # ara_dinlenme değerini kontrol et
                if sm.ara_dinlenme is not None:
                    float(sm.ara_dinlenme)
                sabit_mesailer.append(sm)
            except (ValueError, TypeError):
                # Problemli kayıtları atla
                continue
    except Exception as e:
        # Eğer veritabanında problem varsa boş liste döndür
        sabit_mesailer = []

    kayit, created = PersonelListesiKayit.objects.get_or_create(
        liste=liste,
        personel=personel,
        defaults={'radyasyon_calisani': False}
    )

    mazeret_kayitlari = MazeretKaydi.objects.filter(
        personel=personel
    ).order_by('-baslangic_tarihi')

    yarim_zamanli_calisma = YarimZamanliCalisma.objects.filter( personel=personel ).first()

    # year ve month'u integer'a çevir
    year = int(year)
    month = int(month)
    
    hesaplama = hesapla_fazla_mesai(kayit, year, month)
    mesai_tanimlari = get_favori_mesailer(user)

    # Onaylı mesaileri disable et
    onayli_mesailer = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month,
        OnayDurumu=True
    )
    disabled_days = [m.MesaiDate.day for m in onayli_mesailer]

    # Resmi tatil ve arefeler
    tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year, TatilTarihi__month=month
    )
    resmi_tatil_gunleri = [
        t.TatilTarihi.day for t in tatiller if t.TatilTipi == 'TAM'
    ]
    arefe_gunleri = [
        t.TatilTarihi.day for t in tatiller if t.ArefeMi
    ]
    
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    
    context = {
        'personel': personel,
        'sabit_mesailer' : sabit_mesailer,
        'gunler': gunler,
        'liste': liste,
        'kayit': kayit,
        'mazeret_kayitlari': mazeret_kayitlari,
        'yarim_zamanli_calisma': yarim_zamanli_calisma,
        'hesaplama': hesaplama,
        'mesai_tanimlari': mesai_tanimlari,
        'year': year,
        'month': month,
        'resmi_tatil_gunleri': resmi_tatil_gunleri,
        'arefe_gunleri': arefe_gunleri,
        'disabled_days': disabled_days,
        'hazir_mesai_ata_url': reverse(
            'mercis657:hazir_mesai_ata',
            args=[personel.PersonelID, liste.id, year, month]
        ),
        'extra_payload': {   # 🔑 toplu_islem ile uyumlu hale getiriyoruz
            'personel_id': personel.PersonelID,
            'liste_id': liste.id
        },
    }
    return render(request, 'mercis657/personel_profil.html', context)


@login_required
@require_POST
def sabit_mesai_guncelle(request):
    """Sabit mesai güncelleme endpoint'i"""
    try:
        data = json.loads(request.body)
        personel_id = data.get('personel_id')
        liste_id = data.get('liste_id')
        sabit_mesai_id = data.get('sabit_mesai_id')
        
        if not personel_id or not liste_id:
            return JsonResponse({'status': 'error', 'message': 'Personel ID ve Liste ID gerekli'})
        
        # Personel ve liste kontrolü
        personel = get_object_or_404(Personel, pk=personel_id)
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        
        # PersonelListesiKayit'ı bul veya oluştur
        kayit, created = PersonelListesiKayit.objects.get_or_create(
            liste=liste,
            personel=personel,
            defaults={'radyasyon_calisani': False}
        )
        
        # Sabit mesai güncelle
        if sabit_mesai_id:
            sabit_mesai = get_object_or_404(SabitMesai, pk=sabit_mesai_id)
            kayit.sabit_mesai = sabit_mesai
        else:
            kayit.sabit_mesai = None
            
        kayit.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Sabit mesai başarıyla güncellendi'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Hata oluştu: {str(e)}'
        })


@login_required
@require_POST
def toplu_sabit_mesai_ata(request, liste_id):
    """Tüm personele sabit mesai durumu atar"""
    try:
        data = json.loads(request.body)
        sabit_mesai_id = data.get('sabit_mesai_id')
        
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        
        # Sabit mesai kontrolü
        sabit_mesai = None
        if sabit_mesai_id:
            sabit_mesai = get_object_or_404(SabitMesai, pk=sabit_mesai_id)
        
        # Tüm personel kayıtlarını güncelle
        updated_count = PersonelListesiKayit.objects.filter(
            liste=liste
        ).update(sabit_mesai=sabit_mesai)
        
        sabit_mesai_text = sabit_mesai.aralik if sabit_mesai else "Hiçbiri"
        
        return JsonResponse({
            'status': 'success',
            'message': f'{updated_count} personelin sabit mesai durumu "{sabit_mesai_text}" olarak güncellendi.',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': f'Hata oluştu: {str(e)}'
        })


@login_required
@login_required
def get_calisma_statusu_list(request, liste_id):
    """Personel listesindeki kayıtları ve çalışma statülerini döner. liste_id parametresi birim_id olarak da kullanılabilir."""
    try:
        year = request.GET.get('year')
        month = request.GET.get('month')
        
        # Eğer yıl ve ay parametreleri varsa, liste_id aslında birim_id'dir.
        if year and month:
            # İlgili birim ve dönem için listeyi bul
            liste = PersonelListesi.objects.filter(
                birim_id=liste_id, 
                yil=year, 
                ay=month
            ).first()
            
            if not liste:
                 return JsonResponse({'status': 'error', 'message': f'{year}/{month} dönemi için personel listesi bulunamadı.'}, status=404)
        else:
            # Direkt liste ID olarak işlem yap
            liste = get_object_or_404(PersonelListesi, pk=liste_id)

        kayitlar = liste.kayitlar.select_related('personel').all().order_by('sira_no', 'personel__PersonelName')
        
        data = []
        for k in kayitlar:
            data.append({
                'personel_id': k.personel.PersonelID,
                'ad_soyad': f"{k.personel.PersonelName} {k.personel.PersonelSurname}",
                'is_gunduz_personeli': k.is_gunduz_personeli
            })
            
        return JsonResponse({'status': 'success', 'data': data, 'actual_liste_id': liste.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def update_calisma_statusu_list(request, liste_id):
    """Personel listesindeki kayıtların çalışma statülerini günceller."""
    try:
        import json
        from .cizelge_kontrol_views import sabit_mesai_kontrol
        
        payload = json.loads(request.body)
        updates = payload.get('updates', []) # List of {personel_id: x, is_gunduz_personeli: bool}
        
        liste = get_object_or_404(PersonelListesi, pk=liste_id)
        
        updated_count = 0
        for item in updates:
            pid = item.get('personel_id')
            status = item.get('is_gunduz_personeli')
            
            if pid is not None and status is not None:
                # is_gunduz_personeli alanını güncelle ve eğer False ise sabit_mesai alanını None yap
                if status == False:
                    cnt = PersonelListesiKayit.objects.filter(liste=liste, personel__PersonelID=pid).update(is_gunduz_personeli=status, sabit_mesai=None)
                else:
                    cnt = PersonelListesiKayit.objects.filter(liste=liste, personel__PersonelID=pid).update(is_gunduz_personeli=status)
                updated_count += cnt
        
        # Statüsü True (Gündüz Personeli) olanlar için sabit mesai kontrolünü çalıştır
        if updated_count > 0:
            sabit_mesai_kontrol(liste, int(liste.yil), int(liste.ay))
                
        return JsonResponse({'status': 'success', 'message': f'{updated_count} kayıt güncellendi.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
