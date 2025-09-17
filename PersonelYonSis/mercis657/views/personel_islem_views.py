from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import datetime, date
import json
from ..models import Personel, PersonelListesi, PersonelListesiKayit, Mesai, Mesai_Tanimlari, ResmiTatil, MazeretKaydi
from ..utils import hesapla_fazla_mesai


@login_required
@require_POST
def hazir_mesai_ata(request, personel_id, liste_id, year, month):
    """Seçilen günlere hazır mesai atar"""
    if not request.user.has_permission('Mesai Onaylayabilir'):
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

    kayit, created = PersonelListesiKayit.objects.get_or_create(
        liste=liste,
        personel=personel,
        defaults={'radyasyon_calisani': False}
    )

    mazeret_kayitlari = MazeretKaydi.objects.filter(
        personel=personel
    ).order_by('-baslangic_tarihi')

    hesaplama = hesapla_fazla_mesai(kayit, year, month)
    mesai_tanimlari = Mesai_Tanimlari.objects.filter(GecerliMesai=True)

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

    context = {
        'personel': personel,
        'liste': liste,
        'kayit': kayit,
        'mazeret_kayitlari': mazeret_kayitlari,
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

