from datetime import datetime, timedelta
from calendar import monthrange
from .models import Mesai, Hizmet, ResmiTatil, Izin

def get_month_days(year, month):
    """Verilen ay için gün listesini döndürür"""
    num_days = monthrange(year, month)[1]
    days = []
    
    # Resmi tatilleri al
    tatiller = {
        tatil.TatilTarihi: tatil
        for tatil in ResmiTatil.objects.filter(
            TatilTarihi__year=year,
            TatilTarihi__month=month
        )
    }
    
    for day in range(1, num_days + 1):
        date = datetime(year, month, day).date()
        tatil = tatiller.get(date)
        
        days.append({
            'date': date,
            'is_weekend': date.weekday() >= 5,
            'is_holiday': bool(tatil),
            'holiday_hours': tatil.Suresi if tatil else 0
        })
    return days

def hesapla_gereken_calisma_suresi(yil, ay):
    """Ay içinde çalışılması gereken süreyi hesaplar"""
    days = get_month_days(yil, ay)
    
    # Hafta içi günlerin toplam süresi ve tatil süreleri
    hafta_ici_saati = sum(
        8 for day in days 
        if not day['is_weekend'] and not day['is_holiday']
    )
    
    yarim_tatil_saati = sum(
        3 for day in days
        if not day['is_weekend'] and day['is_holiday'] and day['holiday_hours'] == 3
    )
    
    return hafta_ici_saati + yarim_tatil_saati

def hesapla_fazla_mesai(personel_id, donem_baslangic):
    """Personelin aylık fazla mesai sürelerini hesaplar"""
    year = donem_baslangic.year
    month = donem_baslangic.month
    
    # Çalışılması gereken süreyi hesapla
    days = get_month_days(year, month)
    gereken_sure = hesapla_gereken_calisma_suresi(year, month)

    # Mesaiden düşülecek izinleri önceden çek
    izinler = Izin.objects.filter(MesaidenDus=True)
    izin_tipleri = {i.IzinID: i.IzinTipi for i in izinler}
    izin_ids = list(izin_tipleri.keys())

    # Personelin ilgili ayda aldığı izinleri çek
    izinli_gunler = {}
    izin_qs = Mesai.objects.filter(
        Personel_id=personel_id,
        MesaiDate__year=year,
        MesaiDate__month=month,
        Izin_id__in=izin_ids,
        SilindiMi=False
    ).select_related('Izin')
    for mesai in izin_qs:
        izinli_gunler[mesai.MesaiDate] = mesai.Izin

    gunluk_detay = {}
    toplam_sure = 0
    bayram_sure = 0

    for day in days:
        date = day['date']
        is_weekend = day['is_weekend']
        is_holiday = day['is_holiday']
        holiday_hours = day['holiday_hours']

        # Mesaiden düş izin kontrolü
        izin = izinli_gunler.get(date)
        if izin:
            # Hafta içi ve resmi tatil değilse 8 saat, hafta içi ve arefe ise 5 saat
            if not is_weekend and not is_holiday:
                ek_sure = 8
            elif not is_weekend and is_holiday and holiday_hours == 3:
                ek_sure = 5
            else:
                ek_sure = 0
            if ek_sure > 0:
                gunluk_detay[date.strftime('%Y-%m-%d')] = {
                    'sure': ek_sure,
                    'izin': izin.IzinTipi
                }
                toplam_sure += ek_sure
            continue  # O gün başka mesai eklenmez

        # Normal mesai hesapla
        mesailer = Mesai.objects.filter(
            Personel_id=personel_id,
            MesaiDate=date,
            SilindiMi=False
        ).prefetch_related('Hizmetler')

        gun_toplam = sum(
            hizmet.get_hizmet_suresi(date.strftime('%Y-%m-%d')) / 60
            for mesai in mesailer
            for hizmet in mesai.Hizmetler.all()
        )

        if gun_toplam > 0:
            gunluk_detay[date.strftime('%Y-%m-%d')] = {
                'sure': gun_toplam
            }
            if is_holiday:
                bayram_sure += gun_toplam
            else:
                toplam_sure += gun_toplam

    # Fazla mesai hesabı
    normal_fazla_mesai = max(0, toplam_sure - gereken_sure)

    return {
        'normal': normal_fazla_mesai,
        'bayram': bayram_sure,
        'riskli_normal': 0,  # TODO: Riskli birim kontrolü eklenecek
        'riskli_bayram': 0,
        'gunluk_detay': gunluk_detay
    }

def hesapla_icap_suresi(personel_id, donem_baslangic):
    """
    Personelin aylık icap sürelerini hesaplar
    Süreler saat cinsinden döndürülür
    """
    year = donem_baslangic.year
    month = donem_baslangic.month
    days = get_month_days(year, month)
    
    sonuc = {
        'normal': 0,
        'bayram': 0,
        'gunluk_detay': {}
    }

    for day in days:
        date = day['date']
        mesailer = Mesai.objects.filter(
            Personel_id=personel_id,
            MesaiDate=date,
            SilindiMi=False,
            Hizmetler__HizmetTipi=Hizmet.ICAP
        ).prefetch_related('Hizmetler')

        gun_toplam = 0
        for mesai in mesailer:
            for hizmet in mesai.Hizmetler.all():
                if hizmet.HizmetTipi == Hizmet.ICAP:
                    sure = hizmet.get_hizmet_suresi(date.strftime('%Y-%m-%d'))
                    gun_toplam += sure / 60  # Dakikayı saate çevir

        # Bayram günü kontrolü eklenecek
        is_bayram = False  # TODO: Resmi tatil kontrolü
        
        if is_bayram:
            sonuc['bayram'] += gun_toplam
        else:
            sonuc['normal'] += gun_toplam

        # Günlük detayı kaydet
        sonuc['gunluk_detay'][date.strftime('%Y-%m-%d')] = gun_toplam

    return sonuc

def hesapla_bildirim_verileri(personel_id, donem_baslangic):
    """Hem mesai hem icap verilerini tek seferde hesaplar"""
    mesai_detay = hesapla_fazla_mesai(personel_id, donem_baslangic)
    icap_detay = hesapla_icap_suresi(personel_id, donem_baslangic)
    
    return {
        'mesai': mesai_detay,
        'icap': icap_detay
    }
