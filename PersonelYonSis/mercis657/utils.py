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
            'stop_suresi': Decimal,
            'riskli_bayram_fazla_mesai': Decimal,
            'riskli_normal_fazla_mesai': Decimal,
            'riskli_bayram_gece_fazla_mesai': Decimal,
            'riskli_normal_gece_fazla_mesai': Decimal
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
            'stop_suresi': 0,
            'riskli_bayram_fazla_mesai': 0,
            'riskli_normal_fazla_mesai': 0,
            'riskli_bayram_gece_fazla_mesai': 0,
            'riskli_normal_gece_fazla_mesai': 0
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
        izin_field = getattr(mesai, 'Izin', None)
        mesai_tarih = getattr(mesai, 'MesaiDate', None)

        if izin_field and mesai_tarih:
            if mesai_tarih.weekday() < 5:  # hafta içi
                is_tatil_gunu = mesai_tarih in tatil_map_month
                if not is_tatil_gunu:
                    per_day = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
                    izin_azaltimi += per_day
                elif tatil_map_month.get(mesai_tarih):
                    izin_azaltimi += Decimal('5.0')

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

    # Sabit mesai ara dinlenme toplamı: hafta içi tatil olmayan çalışılan her gün için
    # ara_dinlenme fiili çalışmaya dahildir ama "çalışılması gereken" süreye sayılmaz.
    # Limiti artırarak dengeliyoruz: fazla mesai = fiili - (limit + ara_din_toplam)
    ara_dinlenme_toplam = Decimal('0.0')
    if sabit_mesai and getattr(sabit_mesai, 'ara_dinlenme', None) and sabit_mesai.ara_dinlenme > 0:
        ara_din_per_gun = Decimal(str(sabit_mesai.ara_dinlenme))
        for mesai in mesailer:
            if (
                mesai.MesaiDate.weekday() < 5
                and mesai.MesaiDate not in tatil_map_month
                and not getattr(mesai, 'Izin', None)
                and mesai.MesaiTanim
                and getattr(mesai.MesaiTanim, 'Saat', None)
            ):
                ara_dinlenme_toplam += ara_din_per_gun

    effective_olmasi_gereken = olmasi_gereken_sure - izin_azaltimi - mazeret_azaltimi + ara_dinlenme_toplam

    # ==========================================
    # YENİ ORTAK HESAPLAMA MANTIĞI
    # ==========================================
    #
    # Tüm mesai segmentleri (stopsuz) tarih sırasına göre işlenir.
    # Her segment şu bilgileri taşır:
    #   - seg_start, seg_end (datetime)
    #   - is_bayram, is_gece (context)
    #   - is_gunduz_08_16: 08:00-16:00 arasında mı?
    #   - duration
    #   - riskli bilgileri
    #
    # Doldurma önceliği:
    #   1. Pass: 08:00-16:00 segmentleri ile effective_olmasi_gereken'i doldur
    #   2. Pass: Kalan limiti diğer segmentlerle (gece + diğer gündüz) doldur
    #
    # Limit dolduktan sonra gelen her segment:
    #   - is_gece → gece fazla mesai (bayram/normal)
    #   - değilse → gündüz fazla mesai (bayram/normal)
    # ==========================================

    # Sabit Mesai Bitiş Saati (Riskli NOBET için)
    sabit_mesai_bitis = None
    if sabit_mesai and sabit_mesai.aralik:
        try:
            parts = sabit_mesai.aralik.strip().split()
            if len(parts) >= 2:
                end_s = parts[1]
                eh, em = map(int, end_s.split(':'))
                sabit_mesai_bitis = time(eh, em)
        except (ValueError, IndexError):
            pass

    # Tüm mesailerden segmentleri çıkar
    all_segments = []  # list of dicts

    for mesai in mesailer:
        if not mesai.MesaiTanim:
            continue

        # Saat tanımlı değilse Sure üzerinden basit segment oluştur (fallback)
        if not mesai.MesaiTanim.Saat:
            if getattr(mesai.MesaiTanim, 'Sure', None):
                sure = Decimal(str(mesai.MesaiTanim.Sure))
                # Fallback: gündüz normal segment kabul et, is_gunduz_08_16=True
                all_segments.append({
                    'seg_start': None,
                    'seg_end': None,
                    'duration': sure,
                    'is_bayram': False,
                    'is_gece': False,
                    'is_gunduz_08_16': True,
                    'mesai': mesai,
                    'risky_duration': sure if mesai.riskli_calisma in (Mesai.RISKLI_TAM, Mesai.RISKLI_NOBET) else Decimal('0.0'),
                })
            continue

        # Mesai aralığını belirle
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

        # Timeline milestones: saat sınırları 0, 8, 13, 16, 20
        # Sabit mesai bitiş saati de milestone olarak eklenir
        milestones = set([start_dt, end_dt])
        d_ptr, end_date = start_dt.date(), end_dt.date()
        while d_ptr <= end_date:
            for h in [0, 8, 13, 16, 20]:
                check_dt = datetime.combine(d_ptr, time(h, 0))
                if start_dt < check_dt < end_dt:
                    milestones.add(check_dt)
            if sabit_mesai_bitis:
                sm_dt = datetime.combine(d_ptr, sabit_mesai_bitis)
                if start_dt < sm_dt < end_dt:
                    milestones.add(sm_dt)
            d_ptr += timedelta(days=1)

        sorted_points = sorted(list(milestones))

        for i in range(len(sorted_points) - 1):
            seg_start, seg_end = sorted_points[i], sorted_points[i + 1]
            mid = seg_start + (seg_end - seg_start) / 2

            # Stop içinde mi?
            in_stop = any(s_start <= mid <= s_end for s_start, s_end in stops_intervals)
            if in_stop:
                continue

            duration = Decimal((seg_end - seg_start).total_seconds() / 3600)
            is_bayram, is_gece = get_context(mid)

            # 1. Pass öncelikli segment mi?
            # Sabit mesaisi olan personelde: sabit mesai aralığı (08:00 - sabit_bitis) içinde
            # Sabit mesaisi yoksa: 08:00-16:00 arası (eski mantık)
            seg_start_t = seg_start.time()
            seg_end_t = seg_end.time()
            if sabit_mesai_bitis:
                # Sabit mesai aralığı içinde: bayram değil, sabit bitiş saatinden önce
                is_gunduz_08_16 = (
                    not is_bayram
                    and not is_gece
                    and seg_start_t >= time(8, 0)
                    and seg_end_t <= sabit_mesai_bitis
                    and seg_start_t < seg_end_t
                )
            else:
                # Sabit mesai yok: 08:00-16:00 arası gündüz segmentler
                is_gunduz_08_16 = (
                    not is_bayram
                    and not is_gece
                    and seg_start_t >= time(8, 0)
                    and seg_end_t <= time(16, 0)
                    and seg_start_t < seg_end_t
                )

            # Riskli süre hesabı
            risky_duration = Decimal('0.0')
            if mesai.riskli_calisma == Mesai.RISKLI_TAM:
                risky_duration = duration
            elif mesai.riskli_calisma == Mesai.RISKLI_NOBET:
                if is_gunduz_personeli:
                    # Gündüz personeli: sabit mesai bitişinden sonrası riskli
                    if mesai.MesaiDate.weekday() < 5 and mesai.MesaiDate not in tatil_map_month:
                        if sabit_mesai_bitis:
                            r_start_dt = datetime.combine(mesai.MesaiDate, sabit_mesai_bitis)
                            r_start = max(seg_start, r_start_dt)
                            r_end = seg_end
                            if r_end > r_start:
                                risky_duration = Decimal((r_end - r_start).total_seconds() / 3600)
                else:
                    # Nöbetli personel: vardiyanın tamamı riskli
                    risky_duration = duration

            all_segments.append({
                'seg_start': seg_start,
                'seg_end': seg_end,
                'duration': duration,
                'is_bayram': is_bayram,
                'is_gece': is_gece,
                'is_gunduz_08_16': is_gunduz_08_16,
                'mesai': mesai,
                'risky_duration': risky_duration,
            })

    # ==========================================
    # İki Pasla Limit Doldurma + Fazla Mesai Hesabı
    # ==========================================

    # Bucketlar: (bayram, gece) -> (fazla, riskli_fazla)
    res_bayram_gece = Decimal('0.0')
    res_bayram_gunduz = Decimal('0.0')
    res_normal_gece = Decimal('0.0')
    res_normal_gunduz = Decimal('0.0')

    res_riskli_bayram_gece = Decimal('0.0')
    res_riskli_bayram_gunduz = Decimal('0.0')
    res_riskli_normal_gece = Decimal('0.0')
    res_riskli_normal_gunduz = Decimal('0.0')

    remaining_limit = effective_olmasi_gereken

    # Her segmentin "limit doldurmada kullanılan" miktarını takip et
    # ki 2. pasda yeniden işlemeyelim
    segment_used_for_limit = [Decimal('0.0')] * len(all_segments)

    # --- 1. PASS: Önce 08:00-16:00 segmentleri ile limiti doldur ---
    for idx, seg in enumerate(all_segments):
        if remaining_limit <= 0:
            break
        if not seg['is_gunduz_08_16']:
            continue
        use = min(remaining_limit, seg['duration'])
        segment_used_for_limit[idx] = use
        remaining_limit -= use

    # --- 2. PASS: Kalan limiti gece ve diğer gündüz segmentlerle doldur ---
    for idx, seg in enumerate(all_segments):
        if remaining_limit <= 0:
            break
        if seg['is_gunduz_08_16']:
            continue  # 1. pasda zaten işlendi
        use = min(remaining_limit, seg['duration'])
        segment_used_for_limit[idx] = use
        remaining_limit -= use

    # --- FAZ MESAI HESABI: Limit üzerinde kalan kısımlar ---
    for idx, seg in enumerate(all_segments):
        used = segment_used_for_limit[idx]
        ot_part = seg['duration'] - used

        if ot_part <= 0:
            continue

        is_bayram = seg['is_bayram']
        is_gece = seg['is_gece']
        risky_duration = seg['risky_duration']

        # Riskli oranı: fazla mesai kısmına düşen riskli süre oranla hesapla
        # (segment içinde used kısmı normal, ot_part fazla mesai - riskli oranı koru)
        if seg['duration'] > 0:
            risky_ratio = risky_duration / seg['duration']
        else:
            risky_ratio = Decimal('0.0')
        risky_ot = ot_part * risky_ratio
        normal_ot = ot_part - risky_ot

        if is_bayram and is_gece:
            res_bayram_gece += normal_ot
            res_riskli_bayram_gece += risky_ot
        elif is_bayram and not is_gece:
            res_bayram_gunduz += normal_ot
            res_riskli_bayram_gunduz += risky_ot
        elif not is_bayram and is_gece:
            res_normal_gece += normal_ot
            res_riskli_normal_gece += risky_ot
        else:
            res_normal_gunduz += normal_ot
            res_riskli_normal_gunduz += risky_ot

    # Fiili çalışma süresi: tüm segmentlerin toplamı
    fiili_calisma_suresi = sum(seg['duration'] for seg in all_segments)
    fazla_mesai = max(Decimal('0.0'), fiili_calisma_suresi - effective_olmasi_gereken)

    # --- BAYRAM AYRIŞTIRMA VE ÖNCELİK MANTIĞI ---
    # 1. Segmentlerden çalışılan tüm bayram sürelerini hesapla
    tot_bayram_gece = Decimal('0.0')
    tot_bayram_gunduz = Decimal('0.0')
    tot_riskli_bayram_gece = Decimal('0.0')
    tot_riskli_bayram_gunduz = Decimal('0.0')

    for seg in all_segments:
        if seg['is_bayram']:
            dur = seg['duration']
            r_dur = seg['risky_duration']
            n_dur = dur - r_dur
            if seg['is_gece']:
                tot_bayram_gece += n_dur
                tot_riskli_bayram_gece += r_dur
            else:
                tot_bayram_gunduz += n_dur
                tot_riskli_bayram_gunduz += r_dur

    # 2. Eski 2-pass mantığından gelen havuzları birleştir
    pool_gunduz_normal = res_normal_gunduz + res_bayram_gunduz
    pool_gece_normal = res_normal_gece + res_bayram_gece
    pool_gunduz_riskli = res_riskli_normal_gunduz + res_riskli_bayram_gunduz
    pool_gece_riskli = res_riskli_normal_gece + res_riskli_bayram_gece

    total_ot_pool = pool_gunduz_normal + pool_gece_normal + pool_gunduz_riskli + pool_gece_riskli
    total_bayram_worked = tot_bayram_gece + tot_bayram_gunduz + tot_riskli_bayram_gece + tot_riskli_bayram_gunduz

    if total_ot_pool <= 0:
        res_bayram_gunduz = res_bayram_gece = res_riskli_bayram_gunduz = res_riskli_bayram_gece = Decimal('0.0')
        res_normal_gunduz = res_normal_gece = res_riskli_normal_gunduz = res_riskli_normal_gece = Decimal('0.0')
    else:
        # Öncelik Bayram Mesaisi: Verebileceğimiz bayram, toplam fazla mesaiyi (total_ot_pool) aşamaz
        bayram_ratio = min(Decimal('1.0'), total_ot_pool / total_bayram_worked if total_bayram_worked > 0 else Decimal('1.0'))
        
        # Kullanıcının çalıştığı bayram sürelerini (üst limite kadar) atayalım
        res_bayram_gunduz = tot_bayram_gunduz * bayram_ratio
        res_bayram_gece = tot_bayram_gece * bayram_ratio
        res_riskli_bayram_gunduz = tot_riskli_bayram_gunduz * bayram_ratio
        res_riskli_bayram_gece = tot_riskli_bayram_gece * bayram_ratio
        
        assigned_bayram = res_bayram_gunduz + res_bayram_gece + res_riskli_bayram_gunduz + res_riskli_bayram_gece
        remaining_ot = total_ot_pool - assigned_bayram
        
        # Kalan fazla mesaiyi 2-pass mantığının oluşturduğu havuz oranlarında normal mesai olarak dağıtıyoruz.
        pool_sum = pool_gunduz_normal + pool_gece_normal + pool_gunduz_riskli + pool_gece_riskli
        if pool_sum > 0:
            res_normal_gunduz = remaining_ot * (pool_gunduz_normal / pool_sum)
            res_normal_gece = remaining_ot * (pool_gece_normal / pool_sum)
            res_riskli_normal_gunduz = remaining_ot * (pool_gunduz_riskli / pool_sum)
            res_riskli_normal_gece = remaining_ot * (pool_gece_riskli / pool_sum)
        else:
            res_normal_gunduz = res_normal_gece = res_riskli_normal_gunduz = res_riskli_normal_gece = Decimal('0.0')


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
        'riskli_bayram_fazla_mesai': res_riskli_bayram_gunduz,
        'riskli_normal_fazla_mesai': res_riskli_normal_gunduz,
        'riskli_bayram_gece_fazla_mesai': res_riskli_bayram_gece,
        'riskli_normal_gece_fazla_mesai': res_riskli_normal_gece,
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
        today_17 = datetime.combine(current_date, time(17, 0))
        today_24 = datetime.combine(next_date, time(0, 0)) # Bu gece yarısı
        next_08  = datetime.combine(next_date, time(8, 0))
        
        # Başlangıç zamanını belirle (Sabit Kurallar)
        # Hafta içi resmi tatil değilse 17-08 arası
        # Hafta içi Arefeyse 13-08 arası
        # Resmi tatil veya haftasonuysa 24 saat (08-08)
        
        is_weekend = current_date.weekday() >= 5
        is_resmi_tatil = current_date in tatil_map
        
        if is_weekend:
            start_dt = today_08
        elif is_resmi_tatil:
            rt = tatil_map[current_date]
            if rt.ArefeMi:
                start_dt = today_13
            else:
                start_dt = today_08
        else:
            start_dt = today_17

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
                else:
                    is_arefe = resmi_tatiller.filter(TatilTarihi=mesai_tarih, ArefeMi=True).exists()
                    if is_arefe:
                        izin_azaltimi += Decimal('5.0')

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

def hesapla_riskli_calisma(personel_listesi_kayit, year, month):
    """
    Personel için toplam riskli çalışma süresini hesaplar (hesapla_fazla_mesai fonksiyonunu kullanır).
    """
    sonuc = hesapla_fazla_mesai(personel_listesi_kayit, year, month)
    total = (
        sonuc.get('riskli_bayram_fazla_mesai', Decimal('0.0')) +
        sonuc.get('riskli_normal_fazla_mesai', Decimal('0.0')) +
        sonuc.get('riskli_bayram_gece_fazla_mesai', Decimal('0.0')) +
        sonuc.get('riskli_normal_gece_fazla_mesai', Decimal('0.0'))
    )
    return total

def duzelt_icap_kayitlari(donem_baslangic):
    """
    Belirtilen dönemdeki tüm bildirimler için icap sürelerini yeniden hesaplar ve günceller.
    Değişen kayıtları raporlar ve excel çıktısı üretir.
    
    Args:
        donem_baslangic (str or date): 'YYYY-MM-DD' formatında string veya date objesi.
    """
    from .models import Bildirim, PersonelListesiKayit
    import pandas as pd
    
    if isinstance(donem_baslangic, str):
        target_date = datetime.strptime(donem_baslangic, '%Y-%m-%d').date()
    else:
        target_date = donem_baslangic

    bildirimler = Bildirim.objects.filter(DonemBaslangic=target_date)
    
    updated_records = []
    total_count = bildirimler.count()
    change_count = 0
    scanned_count = 0
    
    print(f"Toplam {total_count} bildirim incelenecek. Dönem: {target_date}")

    for b in bildirimler:
        scanned_count += 1
        
        # PersonelListesiKayit bul
        plk = PersonelListesiKayit.objects.filter(
            liste=b.PersonelListesi,
            personel=b.Personel
        ).first()
        
        if not plk:
            print(f"Kayıt bulunamadı: {b.Personel} - {b.PersonelListesi}")
            continue
            
        # Icap Hesaplama
        sonuc = hesapla_icap_suresi(plk, target_date.year, target_date.month)
        
        yeni_normal = sonuc['normal_icap']
        yeni_bayram = sonuc['bayram_icap']
        yeni_detay = sonuc['icap_detay']
        
        # Değişiklik Kontrolü
        diff = False
        
        # Decimal karşılaştırma
        if abs(b.NormalIcap - yeni_normal) > Decimal('0.01'):
            diff = True
        elif abs(b.BayramIcap - yeni_bayram) > Decimal('0.01'):
            diff = True
        # Detay kontrolü (basit string/json comparison)
        elif b.IcapDetay != yeni_detay:
             diff = True

        if diff:
            old_normal = b.NormalIcap
            old_bayram = b.BayramIcap
            
            b.NormalIcap = yeni_normal
            b.BayramIcap = yeni_bayram
            b.IcapDetay = yeni_detay
            b.save()
            
            change_count += 1
            updated_records.append({
                'Personel': f"{b.Personel.PersonelName} {b.Personel.PersonelSurname}",
                'Eski Normal Icap': float(old_normal),
                'Yeni Normal Icap': float(yeni_normal),
                'Eski Bayram Icap': float(old_bayram),
                'Yeni Bayram Icap': float(yeni_bayram)
            })
            
    print(f"İşlem Tamamlandı.")
    print(f"İncelenen Kayıt Sayısı: {scanned_count}")
    print(f"Değişen Kayıt Sayısı: {change_count}")
    
    if updated_records:
        try:
            df = pd.DataFrame(updated_records)
            output_file = f"icap_duzeltme_raporu_{target_date}.xlsx"
            df.to_excel(output_file, index=False)
            print(f"Excel raporu oluşturuldu: {output_file}")
            return output_file
        except Exception as e:
            print(f"Excel raporu oluşturulurken hata: {e}")
            return None
    else:
        print("Herhangi bir değişiklik yapılmadı.")
        return None