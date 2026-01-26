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
    tatil_map_genis = {rt.TatilTarihi: rt.ArefeMi for rt in resmi_tatiller_genis}

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
    ).select_related('MesaiTanim').prefetch_related('mercis657_stoplar')

    def get_context(dt):
        """Verilen datetime için status döner: is_bayram, is_gece"""
        d = dt.date()
        t = dt.time()
        
        # Gece: 20:00 - 08:00
        is_gece = (t >= time(20, 0)) or (t < time(8, 0))
        
        is_bayram = False
        if d in tatil_map_genis:
            arefe_mi = tatil_map_genis[d]
            if arefe_mi:
                # Arefe günü 13:00'den sonra bayram
                if t >= time(13, 0):
                    is_bayram = True
            else:
                is_bayram = True
                
        return is_bayram, is_gece

    # Sabit mesai düşümü için kullanılacak toplam
    sabit_mesai_dusum_miktari = Decimal('0.0')

    for mesai in mesailer:
        # İzin hesabı
        izin_field = getattr(mesai, 'Izin', None)
        mesai_tarih = getattr(mesai, 'MesaiDate', None)
        
        if izin_field and mesai_tarih:
            if mesai_tarih.weekday() < 5:  # hafta içi
                is_tatil_gunu = mesai_tarih in tatil_map_month
                if not is_tatil_gunu:
                    per_day = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
                    izin_azaltimi += per_day

        if not mesai.MesaiTanim or not mesai.MesaiTanim.Saat:
            continue

        # Mesai zaman aralığını belirle
        try:
            saat_str = mesai.MesaiTanim.Saat.strip()
            start_s, end_s = saat_str.split()
            sh, sm = map(int, start_s.split(':'))
            eh, em = map(int, end_s.split(':'))
            
            start_dt = datetime.combine(mesai_tarih, time(sh, sm))
            end_dt = datetime.combine(mesai_tarih, time(eh, em))
            
            # Bitiş başlangıçtan küçükse veya sarkıyorsa sonraki gün
            if getattr(mesai.MesaiTanim, 'SonrakiGuneSarkiyor', False) or end_dt <= start_dt:
                end_dt += timedelta(days=1)
                
        except ValueError:
            continue

        # Stopları işle: Stopları birer 'negatif aralık' gibi düşünebiliriz ama
        # basitçe Work aralıklarını Stop aralıklarıyla bölmek daha doğru.
        # Bu karmaşık olabileceğinden, basitçe 'Stop Suresi'ni kaydedip,
        # hangi bucket'tan düşeceğimize karar verelim.
        # Stoplar kesin saatli olduğu için bucket'ı bellidir.
        
        stopler = list(mesai.mercis657_stoplar.all())
        stops_intervals = []
        for stop in stopler:
            if stop.StopBaslangic and stop.StopBitis:
                sb = stop.StopBaslangic
                se = stop.StopBitis
                # Stop tarihini belirlemek lazım.
                # Mesai başlangıcına göre hizalanmalı.
                # Stop saati < Mesai başlama saati -> Ertesi gün (kabaca)
                # Daha güvenlisi: Stop saati ile Mesai aralığını kıyaslamak.
                # Genelde stop shift içinde olur.
                
                # Stop başlangıç dt
                stop_start_dt = datetime.combine(mesai_tarih, sb)
                if stop_start_dt < start_dt:
                     stop_start_dt += timedelta(days=1)
                
                stop_end_dt = datetime.combine(mesai_tarih, se)
                if stop_end_dt < stop_start_dt:
                    stop_end_dt += timedelta(days=1)
                
                # Mesai sınırları dışına taşarsa kırp
                stop_start_dt = max(start_dt, stop_start_dt)
                stop_end_dt = min(end_dt, stop_end_dt)
                
                if stop_end_dt > stop_start_dt:
                    stops_intervals.append((stop_start_dt, stop_end_dt))
                    duration_hours = Decimal((stop_end_dt - stop_start_dt).total_seconds() / 3600)
                    stop_suresi += duration_hours

        # Çalışma aralığını (start_dt, end_dt) stoplar haricinde dilimlere böl
        # Basit "Timeline" algoritması
        milestones = set()
        milestones.add(start_dt)
        milestones.add(end_dt)
        
        # Kritik saatler (00:00, 08:00, 13:00, 20:00)
        # Shift'in kapsadığı günleri bul
        d_ptr = start_dt.date()
        end_date = end_dt.date()
        while d_ptr <= end_date:
            for h in [0, 8, 13, 20]:
                check_dt = datetime.combine(d_ptr, time(h, 0))
                if start_dt < check_dt < end_dt:
                    milestones.add(check_dt)
            d_ptr += timedelta(days=1)
            
        # Stop noktalarını da ekle
        for s_start, s_end in stops_intervals:
            # Stop aralığını işten çıkaracağız.
            # Milestones'a ekleyip, segment logic'te "Is inside stop?" kontrolü yapabiliriz.
            if start_dt < s_start < end_dt: milestones.add(s_start)
            if start_dt < s_end < end_dt: milestones.add(s_end)

        sorted_points = sorted(list(milestones))
        
        # Segmentleri işle
        for i in range(len(sorted_points) - 1):
            seg_start = sorted_points[i]
            seg_end = sorted_points[i+1]
            mid = seg_start + (seg_end - seg_start) / 2
            
            # Bu segment bir STOP içinde mi?
            in_stop = False
            for s_start, s_end in stops_intervals:
                if s_start <= mid <= s_end:
                    in_stop = True
                    break
            
            if in_stop:
                continue
                
            # Değilse, bu segment çalışmadır.
            duration = Decimal((seg_end - seg_start).total_seconds() / 3600)
            is_bayram, is_gece = get_context(mid)
            
            if is_bayram and is_gece:
                bucket_bayram_gece += duration
            elif is_bayram and not is_gece:
                bucket_bayram_gunduz += duration
            elif not is_bayram and is_gece:
                bucket_normal_gece += duration
            else:
                bucket_normal_gunduz += duration

        # Sabit Mesai Ara Dinlenme Kontrolü
        # Fiili süreden düş, ama hangi buckettan? 
        # Genelde normal gündüzden düşülür.
        if sabit_mesai and mesai.MesaiTanim.Sure > 8 and mesai.MesaiDate.weekday() < 5:
             # Bu düşüm, hesaplanan "timeline" süresinden ayrıca düşülmeli mi?
             # utils.py orijinal mantığı: fiili süreden direkt düşüyordu.
             # Biz burada bucketları topluyoruz. Toplam fiili bucketların toplamı olacak.
             # Bu yüzden bucketlardan birinden düşmeliyiz.
             dusum = sabit_mesai.ara_dinlenme
             sabit_mesai_dusum_miktari += dusum
             
             # Düşümü uygula (Önce normal gündüz, sonra normal gece...)
             remaining_dusum = dusum
             if bucket_normal_gunduz >= remaining_dusum:
                 bucket_normal_gunduz -= remaining_dusum
                 remaining_dusum = 0
             else:
                 remaining_dusum -= bucket_normal_gunduz
                 bucket_normal_gunduz = Decimal(0)
                 
                 # Hala düşülecek varsa diğerlerine bak (pek olası değil ama)
                 if bucket_normal_gece >= remaining_dusum:
                     bucket_normal_gece -= remaining_dusum
                     remaining_dusum = 0
                 # ... diğerleri ...
    
    # 3. Mazeret Ekleme
    # Mazeret fiili süreye ekleniyor (çalışmış gibi)
    # Hangi bucket? Mazeret genellikle 'Normal Gündüz' sayılır.
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
            if curr.weekday() < 5:
                # Resmi tatil/Arefe değilse
                if curr not in tatil_map_month:
                    # O gün izinli değilse
                    izinli_mi = Mesai.objects.filter(
                        Personel=personel,
                        MesaiDate=curr
                    ).exclude(Izin=False).exclude(Izin__isnull=True).exists()
                    if not izinli_mi:
                        mazeret_gunleri += 1
            curr += timedelta(days=1)
        
        mazeret_azaltimi += mazeret_gunleri * mazeret.gunluk_azaltim_saat

    # Mazereti "Normal Çalışma" olarak ekle
    # (Fiili süreyi artırır, fazla mesai havuzuna girer)
    bucket_normal_gunduz += mazeret_azaltimi

    # 4. Toplamların Hesaplanması
    fiili_calisma_suresi = (
        bucket_bayram_gece + 
        bucket_bayram_gunduz + 
        bucket_normal_gece + 
        bucket_normal_gunduz
    )
    
    # İzin düşümü (olması gerekenden)
    olmasi_gereken_sure -= izin_azaltimi
    
    fazla_mesai = fiili_calisma_suresi - olmasi_gereken_sure
    
    # 5. Dağıtım (Fazla Mesai Varsa)
    # Sıralama: Bayram Gece -> Bayram Gündüz -> Normal Gece -> Normal Gündüz
    res_bayram_gece = Decimal('0.0')
    res_bayram_gunduz = Decimal('0.0')
    res_normal_gece = Decimal('0.0')
    res_normal_gunduz = Decimal('0.0')
    
    if fazla_mesai > 0:
        remaining = fazla_mesai
        
        # 1. Bayram Gece
        take = min(remaining, bucket_bayram_gece)
        res_bayram_gece = take
        remaining -= take
        
        # 2. Bayram Gündüz
        if remaining > 0:
            take = min(remaining, bucket_bayram_gunduz)
            res_bayram_gunduz = take
            remaining -= take
            
        # 3. Normal Gece
        if remaining > 0:
            take = min(remaining, bucket_normal_gece)
            res_normal_gece = take
            remaining -= take
            
        # 4. Kalan (Normal Gündüz)
        if remaining > 0:
            res_normal_gunduz = remaining
            
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
        'stop_suresi': stop_suresi
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
    fiili_calisma_suresi += mazeret_azaltimi

    # İzin azaltımını olması gereken süreden düş
    olmasi_gereken_sure -= izin_azaltimi

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