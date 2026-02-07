from datetime import date, timedelta, datetime, time
from decimal import Decimal
import calendar
from django.db import models
from .models import ResmiTatil, MazeretKaydi, Mesai, Mesai_Tanimlari, SabitMesai, UserMesaiFavori, YarimZamanliCalisma


def hesapla_fazla_mesai(personel_listesi_kayit, year, month):
    """
    Personel için aylık fazla mesai hesaplar.
    
    Args:
        personel_listesi_kayit: PersonelListesiKayit instance
        year: Yıl
        month: Ay
        
    Returns:
        dict: {
            'olması_gereken_sure': Decimal,
            'fiili_calisma_suresi': Decimal,
            'fazla_mesai': Decimal,
            'calisma_gunleri': int,
            'arefe_gunleri': int,
            'mazeret_azaltimi': Decimal,
            'bayram_fazla_mesai': Decimal,       # Bayram Gündüz
            'normal_fazla_mesai': Decimal,       # Normal Gündüz
            'bayram_gece_fazla_mesai': Decimal,  # Bayram Gece
            'normal_gece_fazla_mesai': Decimal,  # Normal Gece
            'stop_suresi': Decimal
        }
    """
    personel = personel_listesi_kayit.personel
    radyasyon_calisani = personel_listesi_kayit.radyasyon_calisani
    sabit_mesai = personel_listesi_kayit.sabit_mesai
    is_gunduz_personeli = getattr(personel_listesi_kayit, 'is_gunduz_personeli', True)
    
    # O dönemdeki yarim_zamanli_calisma durumu
    ilk_gun = date(year, month, 1)
    # Ayın son günü
    days_in_month = calendar.monthrange(year, month)[1]
    son_gun = date(year, month, days_in_month)

    yarim_zamanli_calisma = YarimZamanliCalisma.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=ilk_gun
    ).filter(
        models.Q(bitis_tarihi__isnull=True) | models.Q(bitis_tarihi__gt=ilk_gun)
    ).first()

    if yarim_zamanli_calisma:
        return {
            'olması_gereken_sure': 0,
            'fiili_calisma_suresi': 0,
            'fazla_mesai': 0,
            'calisma_gunleri': 0,
            'arefe_gunleri': 0,
            'mazeret_azaltimi': 0,
            'bayram_fazla_mesai': 0,
            'normal_fazla_mesai': 0,
            'bayram_gece_fazla_mesai': 0,
            'normal_gece_fazla_mesai': 0,
            'stop_suresi': 0
        }

    # ==========================================
    # 1. Olması Gereken Süre Hesabı
    # ==========================================
    calisma_gunleri = 0
    arefe_gunleri = 0

    # Resmi tatilleri cache'le (Ay boyu)
    resmi_tatiller_q = ResmiTatil.objects.filter(
        TatilTarihi__year=year,
        TatilTarihi__month=month
    )
    # Tarih -> ArefeMi
    tatil_map_month = {rt.TatilTarihi: rt.ArefeMi for rt in resmi_tatiller_q}

    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        weekday = current_date.weekday()

        if weekday < 5:  # Pazartesi-Cuma
            is_resmi_tatil = current_date in tatil_map_month
            if not is_resmi_tatil:
                calisma_gunleri += 1
            
            # Arefe kontrolü (ResmiTatil tablosunda varsa)
            if is_resmi_tatil and tatil_map_month[current_date]:
                arefe_gunleri += 1

    gunluk_saat = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
    normal_calisma_suresi = calisma_gunleri * gunluk_saat
    arefe_arttirimi = arefe_gunleri * Decimal('5.0')
    olmasi_gereken_sure = normal_calisma_suresi + arefe_arttirimi

    # ==========================================
    # 2. Fiili Çalışma ve Detaylı Dağılım
    # ==========================================
    
    # Genişletilmiş Tatil Map (Sarkmalar için +2 gün)
    extended_end = son_gun + timedelta(days=2)
    resmi_tatiller_genis = ResmiTatil.objects.filter(
        TatilTarihi__gte=ilk_gun,
        TatilTarihi__lte=extended_end
    )
    tatil_map_genis = {
        rt.TatilTarihi: {'ArefeMi': rt.ArefeMi, 'BayramMi': rt.BayramMi}
        for rt in resmi_tatiller_genis
    }

    bucket_bayram_gece = Decimal('0.0')
    bucket_bayram_gunduz = Decimal('0.0')
    bucket_normal_gece = Decimal('0.0')
    bucket_normal_gunduz = Decimal('0.0')
    
    stop_suresi = Decimal('0.0')
    fiili_calisma_suresi = Decimal('0.0')
    izin_azaltimi = Decimal('0.0')

    mesailer = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month
    ).select_related('MesaiTanim').prefetch_related('mercis657_stoplar').order_by('MesaiDate')

    def get_context(dt):
        """Verilen datetime için status döner: is_bayram, is_gece"""
        d = dt.date()
        t = dt.time()
        
        # Gece: 20:00 - 08:00
        is_gece = (t >= time(20, 0)) or (t < time(8, 0))
        
        is_bayram = False
        if d in tatil_map_genis:
            info = tatil_map_genis[d]
            arefe_mi = info['ArefeMi']
            bayram_mi = info['BayramMi']
            
            if arefe_mi:
                # Arefe günü 13:00'den sonra bayram
                if t >= time(13, 0) and bayram_mi:
                    is_bayram = True
            else:
                if bayram_mi:
                    is_bayram = True
                
        return is_bayram, is_gece



    # İzin Azaltımı Hesapla (Ortak)
    for mesai in mesailer:
        # Fiili çalışma süresine ekleme
        if mesai.MesaiTanim and getattr(mesai.MesaiTanim, 'Sure', None):
            if sabit_mesai and mesai.MesaiTanim.Sure > 8 and mesai.MesaiDate.weekday() < 5:
                fiili_calisma_suresi -= sabit_mesai.ara_dinlenme
            fiili_calisma_suresi += mesai.MesaiTanim.Sure
        izin_field = getattr(mesai, 'Izin', None)
        mesai_tarih = getattr(mesai, 'MesaiDate', None)
        
        if izin_field and mesai_tarih:
            if mesai_tarih.weekday() < 5:  # hafta içi
                is_tatil_gunu = mesai_tarih in tatil_map_month
                if not is_tatil_gunu:
                    per_day = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
                    izin_azaltimi += per_day

    # 3. Mazeret Hesapla (Ortak - Erken hesaplama gerekli)
    mazeret_azaltimi = Decimal('0.0')
    mazeret_kayitlari = MazeretKaydi.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=son_gun,
        bitis_tarihi__gte=ilk_gun
    )
    for mazeret in mazeret_kayitlari:
        baslangic = max(mazeret.baslangic_tarihi, ilk_gun)
        bitis = min(mazeret.bitis_tarihi, son_gun)
        mazeret_gunleri = 0
        curr = baslangic
        while curr <= bitis:
            if curr.weekday() < 5 and curr not in tatil_map_month:
                 izinli_mi = Mesai.objects.filter(Personel=personel, MesaiDate=curr).exclude(Izin=False).exclude(Izin__isnull=True).exists()
                 if not izinli_mi:
                     mazeret_gunleri += 1
            curr += timedelta(days=1)
        mazeret_azaltimi += mazeret_gunleri * mazeret.gunluk_azaltim_saat

    # İzin düşümü (olması gerekenden)
    effective_olmasi_gereken = olmasi_gereken_sure - izin_azaltimi - mazeret_azaltimi


    if is_gunduz_personeli:
        # ----------------------------------------------------------------
        # GÜNDÜZ PERSONELİ (Mevcut Mantık: Bucket Havuzu)
        # ----------------------------------------------------------------
        # Mazereti havuza ekle
        # bucket_normal_gunduz += mazeret_azaltimi
        
        for mesai in mesailer:
            if not mesai.MesaiTanim or not mesai.MesaiTanim.Saat:
                continue
            
            # Zaman aralığı bul
            try:
                saat_str = mesai.MesaiTanim.Saat.strip()
                start_s, end_s = saat_str.split()
                sh, sm = map(int, start_s.split(':'))
                eh, em = map(int, end_s.split(':'))
                if sh == 24: sh = 0
                if eh == 24: eh = 0
                start_dt = datetime.combine(mesai.MesaiDate, time(sh, sm))
                end_dt = datetime.combine(mesai.MesaiDate, time(eh, em))
                if getattr(mesai.MesaiTanim, 'SonrakiGuneSarkiyor', False) or end_dt <= start_dt:
                    end_dt += timedelta(days=1)
            except ValueError:
                continue

            # Stopları işle
            stopler = list(mesai.mercis657_stoplar.all())
            stops_intervals = []
            for stop in stopler:
                if stop.StopBaslangic and stop.StopBitis:
                    sb, se = stop.StopBaslangic, stop.StopBitis
                    stop_start_dt = datetime.combine(mesai.MesaiDate, sb)
                    if stop_start_dt < start_dt: stop_start_dt += timedelta(days=1)
                    stop_end_dt = datetime.combine(mesai.MesaiDate, se)
                    if stop_end_dt < stop_start_dt: stop_end_dt += timedelta(days=1)
                    stop_start_dt = max(start_dt, stop_start_dt)
                    stop_end_dt = min(end_dt, stop_end_dt)
                    if stop_end_dt > stop_start_dt:
                        stops_intervals.append((stop_start_dt, stop_end_dt))
                        stop_suresi += Decimal((stop_end_dt - stop_start_dt).total_seconds() / 3600)

            # Timeline analizi
            milestones = set([start_dt, end_dt])
            d_ptr, end_date = start_dt.date(), end_dt.date()
            while d_ptr <= end_date:
                for h in [0, 8, 13, 20]:
                    check_dt = datetime.combine(d_ptr, time(h, 0))
                    if start_dt < check_dt < end_dt: milestones.add(check_dt)
                d_ptr += timedelta(days=1)
            
            sorted_points = sorted(list(milestones))
            for i in range(len(sorted_points) - 1):
                seg_start, seg_end = sorted_points[i], sorted_points[i+1]
                mid = seg_start + (seg_end - seg_start) / 2
                
                in_stop = any(s_start <= mid <= s_end for s_start, s_end in stops_intervals)
                if in_stop: continue
                    
                duration = Decimal((seg_end - seg_start).total_seconds() / 3600)
                is_bayram, is_gece = get_context(mid)
                
                if is_bayram and is_gece: bucket_bayram_gece += duration
                elif is_bayram and not is_gece: bucket_bayram_gunduz += duration
                elif not is_bayram and is_gece: bucket_normal_gece += duration
                else: bucket_normal_gunduz += duration


        fazla_mesai = fiili_calisma_suresi - effective_olmasi_gereken
        
        # Dağıtım (Best Benefit)
        res_bayram_gece, res_bayram_gunduz = Decimal('0.0'), Decimal('0.0')
        res_normal_gece, res_normal_gunduz = Decimal('0.0'), Decimal('0.0')
        
        if fazla_mesai > 0:
            rem = fazla_mesai
            take = min(rem, bucket_bayram_gece)
            res_bayram_gece = take
            rem -= take
            if rem > 0:
                take = min(rem, bucket_bayram_gunduz)
                res_bayram_gunduz = take
                rem -= take
            if rem > 0:
                take = min(rem, bucket_normal_gece)
                res_normal_gece = take
                rem -= take
            if rem > 0:
                res_normal_gunduz = rem

    else:
        # ----------------------------------------------------------------
        # NÖBETLİ ÇALIŞAN (Kronolojik Hesaplama)
        # ----------------------------------------------------------------
        # Mazereti başlangıç working accumulation olarak kabul ediyoruz
        accumulated_hours = Decimal('0.0')
        limit = effective_olmasi_gereken
        
        # Fazla mesai bucketları (Bunlar direkt olarak sonuç olacak)
        res_bayram_gece = Decimal('0.0')
        res_bayram_gunduz = Decimal('0.0')
        res_normal_gece = Decimal('0.0')
        res_normal_gunduz = Decimal('0.0')
        
        for mesai in mesailer:
            if not mesai.MesaiTanim:
                continue

            # Eğer Saat tanımlı değilse, Süre üzerinden hesapla (Fallback)
            if not mesai.MesaiTanim.Saat:
                if getattr(mesai.MesaiTanim, 'Sure', None):
                    sure = mesai.MesaiTanim.Sure
                    accumulated_hours += sure
                    
                    # Limit aşımı kontrolü (Basit)
                    if accumulated_hours > limit:
                        excess = accumulated_hours - limit
                        ot_part = min(excess, sure)
                        res_normal_gunduz += ot_part
                continue
                
            # Mesai aralığını belirle (Saat tanımlıysa)
            try:
                saat_str = mesai.MesaiTanim.Saat.strip()
                start_s, end_s = saat_str.split()
                sh, sm = map(int, start_s.split(':'))
                eh, em = map(int, end_s.split(':'))
                if sh == 24: sh = 0
                if eh == 24: eh = 0
                start_dt = datetime.combine(mesai.MesaiDate, time(sh, sm))
                end_dt = datetime.combine(mesai.MesaiDate, time(eh, em))
                if getattr(mesai.MesaiTanim, 'SonrakiGuneSarkiyor', False) or end_dt <= start_dt:
                    end_dt += timedelta(days=1)
            except ValueError:
                continue

            # Stopları belirle
            stops_intervals = []
            stopler = list(mesai.mercis657_stoplar.all())
            for stop in stopler:
                if stop.StopBaslangic and stop.StopBitis:
                    sb, se = stop.StopBaslangic, stop.StopBitis
                    stop_start_dt = datetime.combine(mesai.MesaiDate, sb)
                    if stop_start_dt < start_dt: stop_start_dt += timedelta(days=1)
                    stop_end_dt = datetime.combine(mesai.MesaiDate, se)
                    if stop_end_dt < stop_start_dt: stop_end_dt += timedelta(days=1)
                    
                    stop_start_dt = max(start_dt, stop_start_dt)
                    stop_end_dt = min(end_dt, stop_end_dt)
                    
                    if stop_end_dt > stop_start_dt:
                        stops_intervals.append((stop_start_dt, stop_end_dt))
                        stop_suresi += Decimal((stop_end_dt - stop_start_dt).total_seconds() / 3600)

            # Bu vardiyayı segmentlere ayır ve işle
            # Ancak önce toplam süresini bulup birikmişe eklemeli, sonra taşma var mı bakmalıyız.
            
            # Vardiyayı timeline parçalarına ayıralım (stopsuz)
            milestones = set([start_dt, end_dt])
            d_ptr, end_date = start_dt.date(), end_dt.date()
            while d_ptr <= end_date:
                for h in [0, 8, 13, 20]:
                    check_dt = datetime.combine(d_ptr, time(h, 0))
                    if start_dt < check_dt < end_dt: milestones.add(check_dt)
                d_ptr += timedelta(days=1)
            
            sorted_points = sorted(list(milestones))
            
            # Bu vardiyanın her bir segmentini kronolojik olarak işle
            for i in range(len(sorted_points) - 1):
                seg_start, seg_end = sorted_points[i], sorted_points[i+1]
                mid = seg_start + (seg_end - seg_start) / 2
                
                # Stop içinde mi?
                in_stop = any(s_start <= mid <= s_end for s_start, s_end in stops_intervals)
                if in_stop: continue
                
                seg_duration = Decimal((seg_end - seg_start).total_seconds() / 3600)
                
                current_acc_start = accumulated_hours
                accumulated_hours += seg_duration
                
                # Limit aşımı kontrolü
                if accumulated_hours > limit:
                     # Bu segmentin bir kısmı veya tamamı fazla mesai
                     excess = accumulated_hours - limit
                     
                     # Eğer önceki birikim zaten limitin üzerindeyse, tüm segment fazla mesai
                     # Değilse, sadece taşan kısım fazla mesai
                     ot_part = min(excess, seg_duration)
                     
                     # OT kısmını analiz et
                     is_bayram, is_gece = get_context(mid)
                     
                     # Normalde segmentin hepsi aynı tiptedir (çünkü milestone'lar kritik saatlerde bölüyor)
                     # Yani OT kısmını direkt current tipte ekleyebiliriz
                     if is_bayram and is_gece: res_bayram_gece += ot_part
                     elif is_bayram and not is_gece: res_bayram_gunduz += ot_part
                     elif not is_bayram and is_gece: res_normal_gece += ot_part
                     else: res_normal_gunduz += ot_part

        fiili_calisma_suresi = accumulated_hours
        fazla_mesai = max(Decimal('0.0'), fiili_calisma_suresi - limit)
            
    return {
        'olması_gereken_sure': olmasi_gereken_sure,
        'fiili_calisma_suresi': fiili_calisma_suresi,
        'fazla_mesai': fazla_mesai,
        'calisma_gunleri': calisma_gunleri,
        'arefe_gunleri': arefe_gunleri,
        'mazeret_azaltimi': mazeret_azaltimi,
        'bayram_fazla_mesai': res_bayram_gunduz,
        'normal_fazla_mesai': res_normal_gunduz,
        'bayram_gece_fazla_mesai': res_bayram_gece,
        'normal_gece_fazla_mesai': res_normal_gece,
        'stop_suresi': stop_suresi,
        **hesapla_icap_suresi(personel_listesi_kayit, year, month)
    }

def hesapla_icap_suresi(personel_listesi_kayit, year, month):
    """
    Personel için aylık icap sürelerini hesaplar.
    RFC-009'a göre:
    - Mesai bitişinden ertesi sabah 08:00'e kadar.
    - Hafta sonu/tatil ise tüm gün (veya mesai yoksa 24 saat).
    - Mesai varsa, mesai bitişinden itibaren hesaplanır.
    """
    personel = personel_listesi_kayit.personel
    days_in_month = calendar.monthrange(year, month)[1]
    
    normal_icap = Decimal('0.0')
    bayram_icap = Decimal('0.0')
    icap_detay = {}
    
    # Resmi tatilleri cache'le
    resmi_tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year,
        TatilTarihi__month=month
    )
    tatil_map = {rt.TatilTarihi: rt for rt in resmi_tatiller}

    # İcap kayıtlarını çek
    icap_kayitlari = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month,
        Icap=True
    ).select_related('MesaiTanim')

    for kayit in icap_kayitlari:
        current_date = kayit.MesaiDate
        next_date = current_date + timedelta(days=1)
        
        # Tatil durumlarını belirle
        is_today_bayram = False
        is_today_arefe = False
        is_next_bayram = False
        
        if current_date in tatil_map:
            rt = tatil_map[current_date]
            if rt.BayramMi:
                 is_today_bayram = True
            elif rt.ArefeMi:
                 is_today_arefe = True
        
        # Ertesi günün tatil durumu (cache'den bulunmayabilir, veritabanından çek)
        # Ancak performans için sadece bu ayı cacheledik. Bir sonraki gün bir sonraki aya düşebilir.
        # Basitlik ve performans için tek tek sorgu yerine genişletilmiş cache veya tekil sorgu.
        # Sonraki gün ayın son günü ise sorun yok, sonraki ayın ilk günü ise mapte yok.
        if next_date in tatil_map:
             rt_next = tatil_map[next_date]
             if rt_next.BayramMi:
                 is_next_bayram = True
        else:
             # Ay geçişi kontrolü
             next_rt = ResmiTatil.objects.filter(TatilTarihi=next_date).first()
             if next_rt and next_rt.BayramMi:
                 is_next_bayram = True

        # Zaman dilimleri
        today_08 = datetime.combine(current_date, time(8, 0))
        today_13 = datetime.combine(current_date, time(13, 0))
        today_24 = datetime.combine(next_date, time(0, 0)) # Bu gece yarısı
        next_08  = datetime.combine(next_date, time(8, 0))
        
        # Başlangıç zamanını belirle
        start_dt = today_08 # Mesai yoksa varsayılan
        
        if kayit.MesaiTanim and kayit.MesaiTanim.Saat:
            try:
                saat_str = kayit.MesaiTanim.Saat.strip()
                _, end_s = saat_str.split()
                eh, em = map(int, end_s.split(':'))
                mesai_bitis = datetime.combine(current_date, time(eh, em))
                
                # Sarkma ve gece yarısı geçişleri
                start_parts = saat_str.split()[0].split(':')
                start_h, start_m = int(start_parts[0]), int(start_parts[1])
                start_time_val = calendar.timegm(datetime.combine(current_date, time(start_h, start_m)).timetuple())
                end_time_val = calendar.timegm(mesai_bitis.timetuple())
                
                if getattr(kayit.MesaiTanim, 'SonrakiGuneSarkiyor', False):
                     mesai_bitis += timedelta(days=1)
                elif end_time_val < start_time_val:
                     mesai_bitis += timedelta(days=1)
                
                # Kural: Icap hesaplaması için mesai bitimi 08:00'dan büyük olmalı
                # Eğer mesai bitişi <= 08:00 ise start_dt 08:00 kalır (User logic interpretation needed).
                # Kullanıcı: "mesai bitiminin 08:00'dan büyük olmak zorunda"
                # Bu şu demek olabilir: Eğer gece vardiyası 08:00'de bitiyorsa icap 08:00'de başlar.
                # Eğer 07:00'de bitiyorsa 08:00'de icap başlar mı? Yoksa 07:00'de mi?
                # "Mesai yoksa" durumu ile benzer.
                # Varsayım: Mesai bitişi > 08:00 ise start_dt = mesai_bitis
                if mesai_bitis > today_08:
                    start_dt = mesai_bitis
                else:
                    start_dt = today_08

            except ValueError:
                pass # Parse hatası, varsayılan 08:00 kalır

        # Bitiş zamanı her zaman ertesi gün 08:00
        end_dt = next_08
        
        if start_dt >= end_dt:
             continue # Geçersiz aralık

        # Süre hesaplama ve dağıtma
        current_cursor = start_dt
        day_bayram_sum = Decimal('0.0')
        day_normal_sum = Decimal('0.0')

        # Kritik eşikler: 13:00 (Arefe), 24:00 (Gece geçişi)
        check_points = sorted([t for t in [today_13, today_24] if current_cursor < t < end_dt])
        # Bitiş noktasını da ekle
        points = check_points + [end_dt]
        
        for p in points:
            if current_cursor >= p:
                continue
            
            segment_duration = Decimal((p - current_cursor).total_seconds() / 3600)
            
            # Bu segmentin türünü belirle
            is_segment_bayram = False
            
            # Period: current_cursor -> p
            mid_point = current_cursor + (p - current_cursor) / 2
            
            # 1. Bugünün kontrolü (08:00 - 24:00 arası)
            if mid_point < today_24:
                if is_today_bayram:
                    is_segment_bayram = True
                elif is_today_arefe:
                    # 13:00 sonrası bayram
                    if mid_point >= today_13:
                        is_segment_bayram = True
                    else:
                        is_segment_bayram = False
                else:
                    is_segment_bayram = False
            # 2. Yarının kontrolü (00:00 - 08:00 arası)
            else:
                if is_next_bayram:
                    is_segment_bayram = True
                else:
                     # Sonraki gün bayram değilse normal icap
                     is_segment_bayram = False
            
            if is_segment_bayram:
                day_bayram_sum += segment_duration
            else:
                day_normal_sum += segment_duration
                
            current_cursor = p
            
        bayram_icap += day_bayram_sum
        normal_icap += day_normal_sum
            
        # Format: 'YYYY-MM-DD' key for the notification detail
        key = current_date.strftime('%Y-%m-%d')
        icap_detay[key] = float(day_bayram_sum + day_normal_sum) # Toplam süreyi yazıyoruz detay olarak

    return {
        'normal_icap': normal_icap,
        'bayram_icap': bayram_icap,
        'toplam_icap': normal_icap + bayram_icap,
        'icap_detay': icap_detay
    }

def get_favori_mesailer(user):
    """Kullanıcının favori mesailerini döndürür. Favori yoksa tüm mesailer gelir."""
    favoriler = UserMesaiFavori.objects.filter(user=user).select_related("mesai").order_by("mesai")
    if favoriler.exists():
        return [f.mesai for f in favoriler]
    return Mesai_Tanimlari.objects.all().order_by("Saat")


def hesapla_fazla_mesai_sade(personel_listesi_kayit, year, month):
    """
    Sadeleştirilmiş fazla mesai hesaplama (bayram mesaisi hariç).
    Anlık hesaplama için kullanılır.
    
    Args:
        personel_listesi_kayit: PersonelListesiKayit instance
        year: Yıl
        month: Ay
        
    Returns:
        Decimal: Fazla mesai değeri (saat cinsinden)
    """
    personel = personel_listesi_kayit.personel
    radyasyon_calisani = personel_listesi_kayit.radyasyon_calisani
    sabit_mesai = personel_listesi_kayit.sabit_mesai
    
    # Yarım zamanlı çalışma kontrolü
    ilk_gun = date(year, month, 1)
    yarim_zamanli_calisma = YarimZamanliCalisma.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=ilk_gun
    ).filter(
        models.Q(bitis_tarihi__isnull=True) | models.Q(bitis_tarihi__gt=ilk_gun)
    ).first()

    if yarim_zamanli_calisma:
        return Decimal('0.0')

    # Aylık gün sayısı ve hafta içi günleri hesapla
    days_in_month = calendar.monthrange(year, month)[1]
    calisma_gunleri = 0
    arefe_gunleri = 0

    # Resmi tatilleri al
    resmi_tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year,
        TatilTarihi__month=month
    )
    
    # Hafta içi günleri say
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        weekday = current_date.weekday()

        if weekday < 5:  # Pazartesi-Cuma
            is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=current_date).exists()
            if not is_resmi_tatil:
                calisma_gunleri += 1

            is_arefe = resmi_tatiller.filter(
                TatilTarihi=current_date,
                ArefeMi=True
            ).exists()
            if is_arefe:
                arefe_gunleri += 1
    
    # Günlük çalışma saati
    gunluk_saat = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')

    # Olması gereken süre hesapla
    normal_calisma_suresi = calisma_gunleri * gunluk_saat
    arefe_arttirimi = arefe_gunleri * Decimal('5.0')
    olmasi_gereken_sure = normal_calisma_suresi + arefe_arttirimi

    # Fiili çalışma süresini hesapla
    fiili_calisma_suresi = Decimal('0.0')

    # O ayki mesai kayıtlarını al
    mesailer = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month
    ).select_related('MesaiTanim').prefetch_related('mercis657_stoplar')

    # İzin kaynaklı azaltım
    izin_azaltimi = Decimal('0.0')
    stop_suresi = Decimal('0.0')

    for mesai in mesailer:
        # Fiili çalışma süresine ekleme
        if mesai.MesaiTanim and getattr(mesai.MesaiTanim, 'Sure', None):
            if sabit_mesai and mesai.MesaiTanim.Sure > 8 and mesai.MesaiDate.weekday() < 5:
                fiili_calisma_suresi -= sabit_mesai.ara_dinlenme
            fiili_calisma_suresi += mesai.MesaiTanim.Sure

        # STOP sürelerini düş
        stopler = list(getattr(mesai, 'mercis657_stoplar').all())
        for stop in stopler:
            try:
                stop_hours = Decimal(str(stop.Sure)) if stop.Sure is not None else Decimal('0.0')
            except Exception:
                stop_hours = Decimal('0.0')
            fiili_calisma_suresi -= stop_hours
            stop_suresi += stop_hours

        # İzin azaltımı
        izin_field = getattr(mesai, 'Izin', None)
        mesai_tarih = getattr(mesai, 'MesaiDate', None)
        if izin_field and mesai_tarih:
            if mesai_tarih.weekday() < 5:  # hafta içi
                is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=mesai_tarih).exists()
                if not is_resmi_tatil:
                    per_day = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
                    izin_azaltimi += per_day

    # Mazeret azaltımını hesapla
    mazeret_azaltimi = Decimal('0.0')
    mazeret_kayitlari = MazeretKaydi.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=date(year, month, days_in_month),
        bitis_tarihi__gte=date(year, month, 1)
    )

    for mazeret in mazeret_kayitlari:
        baslangic = max(mazeret.baslangic_tarihi, date(year, month, 1))
        bitis = min(mazeret.bitis_tarihi, date(year, month, days_in_month))

        mazeret_gunleri = 0
        current_date = baslangic
        while current_date <= bitis:
            if current_date.weekday() < 5:  # Hafta içi
                is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=current_date).exists()
                if not is_resmi_tatil:
                    izinli_mi = Mesai.objects.filter(
                        Personel=personel,
                        MesaiDate=current_date
                    ).exclude(Izin=False).exclude(Izin__isnull=True).exists()
                    if not izinli_mi:
                        mazeret_gunleri += 1
            current_date += timedelta(days=1)

        mazeret_azaltimi += mazeret_gunleri * mazeret.gunluk_azaltim_saat

    # Mazeret azaltımı fiili çalışma süresine ekleniyor
    # fiili_calisma_suresi += mazeret_azaltimi

    # İzin azaltımını olması gereken süreden düş
    olmasi_gereken_sure -= (izin_azaltimi + mazeret_azaltimi)

    # Fazla mesai hesapla
    fazla_mesai = fiili_calisma_suresi - olmasi_gereken_sure

    return fazla_mesai


def get_vardiya_tanimlari():
    """
    Tüm mesai tanımlarının vardiya bilgilerini döndürür.
    
    Returns:
        dict: { mesai_id: { 'gunduz': bool, 'aksam': bool, 'gece': bool } }
    """
    mesai_tanimlari = Mesai_Tanimlari.objects.all()
    result = {}
    for mt in mesai_tanimlari:
        result[mt.id] = {
            'gunduz': mt.GunduzMesaisi,
            'aksam': mt.AksamMesaisi,
            'gece': mt.GeceMesaisi
        }
    return result

def get_turkish_month_name(month_index):
    """
    Ay indeksine göre Türkçe ay ismini döndürür.
    1 -> Ocak
    """
    months = [
        "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
        "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
    ]
    try:
        m = int(month_index)
        if 1 <= m <= 12:
            return f"{months[m]} Ayı"
    except (ValueError, TypeError):
        pass
    return f"{month_index}. Dönem"