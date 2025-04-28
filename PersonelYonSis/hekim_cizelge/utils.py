from datetime import datetime, timedelta, time
from calendar import monthrange
from .models import Mesai, Hizmet, ResmiTatil, Izin
from django.db.models import Q

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

def get_bayram_info(year, month):
    """
    Gets bayram info relevant to the given month.
    Returns:
        - month_bayram_dates: List of date objects for bayram days *in* this month.
        - month_arefe_date: Date object for arefe day *in* this month, or None.
        - bayram_last_days: Dict mapping {bayram_adi: last_date_object} for all bayrams touching this year.
        - date_to_bayram_adi: Dict mapping {date_object: bayram_adi} for dates in this month.
    """
    # Fetch all bayram/arefe for the year for context
    # Q importu gerekebilir: from django.db.models import Q
    all_holidays = ResmiTatil.objects.filter(
        (Q(BayramMi=True) | Q(ArefeMi=True)),
        TatilTarihi__year=year
    ).order_by('TatilTarihi')

    bayram_sequences = {}
    date_to_bayram_adi_map = {}
    for holiday in all_holidays:
        # Use BayramAdi if available, otherwise generate one (e.g., for single-day holidays marked BayramMi)
        # Boş BayramAdi yerine Aciklama kullanmak daha güvenli olabilir
        key = holiday.BayramAdi if holiday.BayramAdi else holiday.Aciklama 
        if not key: continue # Eğer hem BayramAdi hem Aciklama boşsa atla

        if key not in bayram_sequences:
            bayram_sequences[key] = []
        bayram_sequences[key].append(holiday.TatilTarihi)
        
        # Map date to adi only if it's in the current month
        if holiday.TatilTarihi.month == month:
             date_to_bayram_adi_map[holiday.TatilTarihi] = key

    bayram_last_days_map = {
        name: dates[-1] for name, dates in bayram_sequences.items() if dates
    }

    # Filter for the current month
    month_holidays = all_holidays.filter(TatilTarihi__month=month)
    month_bayram_dates = [h.TatilTarihi for h in month_holidays if h.BayramMi]
    month_arefe_holiday = month_holidays.filter(ArefeMi=True).first()
    month_arefe_date = month_arefe_holiday.TatilTarihi if month_arefe_holiday else None

    return month_bayram_dates, month_arefe_date, bayram_last_days_map, date_to_bayram_adi_map

def get_bayram_gunleri(yil, ay):
    """Ay içindeki bayram günlerini ve arefe gününü döndürür"""
    tatiller = list(ResmiTatil.objects.filter(
        TatilTarihi__year=yil,
        TatilTarihi__month=ay,
        BayramMi=True
    ).order_by('TatilTarihi'))

    arefe = ResmiTatil.objects.filter(
        TatilTarihi__year=yil,
        TatilTarihi__month=ay,
        ArefeMi=True
    ).first()

    bayram_gunleri = [t.TatilTarihi for t in tatiller]
    arefe_gunu = arefe.TatilTarihi if arefe else None
    return bayram_gunleri, arefe_gunu

def bol_nobet_suresi_arefe(hizmet_suresi):
    """
    Arefe günü başlayan 24 saatlik nöbetin süresini böler (19 bayram, 5 normal).
    - hizmet_suresi: dakika cinsinden
    - Dönüş: (bayram_saat, normal_saat)
    """
    hizmet_saat = hizmet_suresi / 60
    if hizmet_saat >= 24:
        return 19, 5 # 19 saat bayram (13:00-08:00), 5 saat normal (08:00-13:00)
    elif hizmet_saat > 0:
        # Oranlama (Genellikle nöbetler 24 saattir, bu kısım nadiren kullanılır)
        oran_bayram = 19 / 24
        oran_normal = 5 / 24
        return hizmet_saat * oran_bayram, hizmet_saat * oran_normal
    else:
        return 0, 0

def bol_nobet_suresi_bayram_son_gun(hizmet_suresi):
    """
    Bayramın SON GÜNÜ tutulan nöbetin süresini böler (16 bayram, 8 normal).
    - hizmet_suresi: dakika cinsinden
    - Dönüş: (bayram_saat, normal_saat)
    """
    hizmet_saat = hizmet_suresi / 60
    if hizmet_saat >= 24:
        return 16, 8 # 16 saat bayram (08:00-24:00), 8 saat normal (00:00-08:00 ertesi gün)
    elif hizmet_saat > 0:
        # Oranlama
        oran_bayram = 16 / 24
        oran_normal = 8 / 24
        return hizmet_saat * oran_bayram, hizmet_saat * oran_normal
    else:
        return 0, 0

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
    """Personelin aylık fazla mesai sürelerini hesaplar (bayram son günü özel)"""
    year = donem_baslangic.year
    month = donem_baslangic.month

    days = get_month_days(year, month)
    gereken_sure = hesapla_gereken_calisma_suresi(year, month)

    izinler = Izin.objects.filter(MesaidenDus=True)
    izin_tipleri = {i.IzinID: i.IzinTipi for i in izinler}
    izin_ids = list(izin_tipleri.keys())

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
    toplam_normal_sure = 0 # Normal gün/saatleri biriktirecek
    toplam_bayram_sure = 0 # Sadece bayram saatlerini biriktirecek

    # Bayram günleri ve arefe tespiti - YENİ YÖNTEM
    bayram_gunleri_in_month, arefe_gunu_in_month, bayram_last_days, date_to_bayram_adi = get_bayram_info(year, month)
    # Eski yöntem: bayram_gunleri, arefe_gunu = get_bayram_gunleri(year, month)
    # Eski yöntem: last_bayram_date = bayram_gunleri[-1] if bayram_gunleri else None # Son bayram gününü önceden al

    for day in days:
        date = day['date']
        is_weekend = day['is_weekend']
        is_holiday = day['is_holiday']
        holiday_hours = day['holiday_hours'] # Arefe için 3, tam gün tatil için 8 vs.

        izin = izinli_gunler.get(date)
        if izin:
            # İzinli günlerde çalışılmış gibi süre ekle (fazla mesai hesabından düşmek için)
            # Sadece hafta içi ve yarım gün tatil olan günler dikkate alınır.
            ek_sure = 0
            if not is_weekend and not is_holiday:
                ek_sure = 8 # Hafta içi tam gün izin
            elif not is_weekend and is_holiday and holiday_hours == 3: # Arefe gibi yarım gün tatillerde izin
                ek_sure = 5 # 8 - 3 = 5 saat çalışılmış gibi
            
            if ek_sure > 0:
                gunluk_detay[date.strftime('%Y-%m-%d')] = {
                    'sure': ek_sure,
                    'izin': izin.IzinTipi,
                    'aciklama': 'İzinli (Normal Süreye Eklendi)'
                }
                toplam_normal_sure += ek_sure # İzin süreleri normal süreye eklenir
            continue # İzinli günlerde başka mesai aranmaz

        mesailer = Mesai.objects.filter(
            Personel_id=personel_id,
            MesaiDate=date,
            SilindiMi=False
        ).prefetch_related('Hizmetler')

        gun_toplam = 0
        gun_bayram = 0
        gun_normal = 0
        gun_aciklamalar = [] # Günlük detay için

        for mesai in mesailer:
            for hizmet in mesai.Hizmetler.all():
                # --- ICAP HİZMETLERİNİ ATLA! ---
                if hizmet.HizmetTipi == Hizmet.ICAP:
                    continue # Fazla mesai hesabına dahil etme, sonraki hizmete geç
                # --------------------------------

                sure = hizmet.get_hizmet_suresi(date.strftime('%Y-%m-%d'))  # dakika
                saat = sure / 60
                hizmet_tipi = hizmet.HizmetTipi

                # is_nobet = (hizmet_tipi == Hizmet.NOBET) # Bu satır tekrar tanımlanıyor, önceki kalabilir
                is_nobet = (hizmet_tipi == Hizmet.NOBET)
                # is_arefe = (date == arefe_gunu) # Eski kontrol
                is_arefe = (date == arefe_gunu_in_month)
                # is_bayram = (date in bayram_gunleri) # Eski kontrol
                is_bayram = (date in bayram_gunleri_in_month)
                # is_last_bayram_day = (date == last_bayram_date) # Eski, daha basit kontrol
                
                # Yeni: Gerçek bayram son günü kontrolü
                is_last_day_of_its_bayram = False
                if is_bayram:
                    current_bayram_adi = date_to_bayram_adi.get(date)
                    if current_bayram_adi:
                        last_day_for_this_bayram = bayram_last_days.get(current_bayram_adi)
                        if date == last_day_for_this_bayram:
                            is_last_day_of_its_bayram = True

                h_bayram = 0
                h_normal = 0
                aciklama = f"{hizmet.HizmetTipi}"

                if is_nobet:
                    aciklama = "Nöbet"
                    if is_arefe:
                        h_bayram, h_normal = bol_nobet_suresi_arefe(sure)
                        aciklama += f" (Arefe: {h_bayram:.2f} saat Bayram, {h_normal:.2f} saat Normal)"
                    elif is_last_day_of_its_bayram: # Yeni kontrol
                        h_bayram, h_normal = bol_nobet_suresi_bayram_son_gun(sure)
                        aciklama += f" (Bayram Sonu: {h_bayram:.2f} saat Bayram, {h_normal:.2f} saat Normal)"
                    elif is_bayram: # Diğer bayram günleri (Arefe değil, son gün değil)
                        h_bayram = saat
                        h_normal = 0
                        aciklama += f" (Bayram: {h_bayram:.2f} saat)"
                    else: # Normal gün nöbeti
                        h_normal = saat
                        aciklama += f" (Normal: {h_normal:.2f} saat)"
                else: # Normal Mesai veya diğer hizmet tipleri (Nöbet değil)
                    # Normal mesailer, bayramda yapılsa bile normal süreye eklenir,
                    # çünkü 'gereken_sure' zaten bayramları düşerek hesaplanmıştır.
                    # Ancak, bayramda yapılan normal mesaiyi ayrı takip etmek gerekebilir diye
                    # gun_bayram'a ekleme mantığını koruyalım (mevcut koddaki gibi).
                    if is_bayram or is_arefe:
                        h_bayram = saat
                        aciklama += f" (Bayram/Arefe Mesai: {h_bayram:.2f} saat Bayram)"
                    else:
                        h_normal = saat
                        aciklama += f" (Normal Mesai: {h_normal:.2f} saat Normal)"

                gun_bayram += h_bayram
                gun_normal += h_normal
                gun_aciklamalar.append(aciklama)
        
        gun_toplam = gun_bayram + gun_normal

        if gun_toplam > 0:
            gunluk_detay[date.strftime('%Y-%m-%d')] = {
                'sure': round(gun_toplam, 2) # Toplam saat
            }
            if gun_bayram > 0:
                gunluk_detay[date.strftime('%Y-%m-%d')]['bayram_sure'] = round(gun_bayram, 2)
            if gun_normal > 0:
                gunluk_detay[date.strftime('%Y-%m-%d')]['normal_sure'] = round(gun_normal, 2)
            if gun_aciklamalar:
                 gunluk_detay[date.strftime('%Y-%m-%d')]['aciklama'] = " | ".join(gun_aciklamalar)

            toplam_bayram_sure += gun_bayram # Sadece bayram/arefe saatlerini topla
            toplam_normal_sure += gun_normal # Normal saatleri (nöbetin normal kısımları dahil) topla

    # Normal fazla mesai: Toplam normal çalışma süresi + izinlerle eklenen süre - gereken süre
    normal_fazla_mesai = max(0, toplam_normal_sure - gereken_sure)

    # Sonuçları yuvarlayalım
    return {
        'normal': round(normal_fazla_mesai, 2),
        'bayram': round(toplam_bayram_sure, 2),
        'riskli_normal': 0, # Bu alanlar henüz hesaplanmıyor
        'riskli_bayram': 0,
        'toplam_calisma_normal': round(toplam_normal_sure, 2), # Bilgi amaçlı eklendi
        'toplam_calisma_bayram': round(toplam_bayram_sure, 2), # Bilgi amaçlı eklendi
        'gereken_calisma': round(gereken_sure, 2), # Bilgi amaçlı eklendi
        'gunluk_detay': gunluk_detay
    }

def hesapla_icap_suresi(personel_id, donem_baslangic):
    """
    Personelin aylık icap sürelerini hesaplar (Arefe/Bayram Sonu özel durumu dahil)
    DÖNÜŞ: {
        'normal': ...,
        'bayram': ...,
        'gunluk_detay': { '2025-04-01': 24.0, ... }  # Sadece gün ve toplam süre
    }
    """
    year = donem_baslangic.year
    month = donem_baslangic.month
    days = get_month_days(year, month)
    
    # Bayram/Arefe bilgisini al
    bayram_gunleri_in_month, arefe_gunu_in_month, bayram_last_days, date_to_bayram_adi = get_bayram_info(year, month)

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
        gun_bayram = 0
        gun_normal = 0

        for mesai in mesailer:
            for hizmet in mesai.Hizmetler.all():
                if hizmet.HizmetTipi == Hizmet.ICAP:
                    sure_dk = hizmet.get_hizmet_suresi(date.strftime('%Y-%m-%d'))
                    saat = sure_dk / 60

                    is_arefe = (date == arefe_gunu_in_month)
                    is_bayram = (date in bayram_gunleri_in_month)
                    is_last_day_of_its_bayram = False
                    if is_bayram:
                        current_bayram_adi = date_to_bayram_adi.get(date)
                        if current_bayram_adi:
                            last_day_for_this_bayram = bayram_last_days.get(current_bayram_adi)
                            if date == last_day_for_this_bayram:
                                is_last_day_of_its_bayram = True
                    
                    h_bayram = 0
                    h_normal = 0

                    if is_arefe:
                        h_bayram, h_normal = bol_nobet_suresi_arefe(sure_dk)
                    elif is_last_day_of_its_bayram:
                        h_bayram, h_normal = bol_nobet_suresi_bayram_son_gun(sure_dk)
                    elif is_bayram:
                        h_bayram = saat
                        h_normal = 0
                    else:
                        h_normal = saat

                    gun_bayram += h_bayram
                    gun_normal += h_normal

        gun_toplam = gun_bayram + gun_normal

        # Sadece sadeleştirilmiş veri: { '2025-04-01': 24.0, ... }
        if gun_toplam > 0:
            sonuc['gunluk_detay'][date.strftime('%Y-%m-%d')] = round(gun_toplam, 2)

        sonuc['bayram'] += gun_bayram
        sonuc['normal'] += gun_normal

    sonuc['normal'] = round(sonuc['normal'], 2)
    sonuc['bayram'] = round(sonuc['bayram'], 2)
    return sonuc

def hesapla_bildirim_verileri(personel_id, donem_baslangic):
    """Hem mesai hem icap verilerini tek seferde hesaplar"""
    mesai_detay = hesapla_fazla_mesai(personel_id, donem_baslangic)
    icap_detay = hesapla_icap_suresi(personel_id, donem_baslangic)
    
    return {
        'mesai': mesai_detay,
        'icap': icap_detay
    }
