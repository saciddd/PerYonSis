from datetime import date, timedelta
from decimal import Decimal
import calendar
from .models import ResmiTatil, MazeretKaydi, Mesai, Mesai_Tanimlari, SabitMesai, UserMesaiFavori


def hesapla_fazla_mesai(personel_listesi_kayit, year, month):
    """
    Personel için aylık fazla mesai hesaplar.
    
    Args:
        personel_listesi_kayit: PersonelListesiKayit instance
        year: Yıl
        month: Ay
        
    Returns:
        dict: {
            'olması_gereken_sure': Decimal,  # saat cinsinden
            'fiili_calisma_suresi': Decimal,  # saat cinsinden
            'fazla_mesai': Decimal,  # saat cinsinden
            'calisma_gunleri': int,
            'arefe_gunleri': int,
            'mazeret_azaltimi': Decimal
            'stop_suresi': Decimal  # saat cinsinden
        }
    """
    personel = personel_listesi_kayit.personel
    radyasyon_calisani = personel_listesi_kayit.radyasyon_calisani
    sabit_mesai = personel_listesi_kayit.sabit_mesai

    # Aylık gün sayısı ve hafta içi günleri hesapla
    days_in_month = calendar.monthrange(year, month)[1]
    calisma_gunleri = 0
    arefe_gunleri = 0

    # Resmi tatilleri al
    resmi_tatiller = ResmiTatil.objects.filter(
        TatilTarihi__year=year,
        TatilTarihi__month=month
    )

    # Hafta içi günleri say (Pazartesi=0, Pazar=6)
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        weekday = current_date.weekday()

        # Hafta içi mi kontrol et
        if weekday < 5:  # Pazartesi-Cuma
            # Resmi tatil mi kontrol et
            is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=current_date).exists()

            if not is_resmi_tatil:
                calisma_gunleri += 1

                # Arefe günü mü kontrol et
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
    # Arefe günleri tüm personeller için -5 saat olacak
    arefe_azaltimi = arefe_gunleri * Decimal('5.0')
    olmasi_gereken_sure = normal_calisma_suresi - arefe_azaltimi

    # Fiili çalışma süresini hesapla
    fiili_calisma_suresi = Decimal('0.0')

    # O ayki mesai kayıtlarını al
    mesailer = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month
    ).select_related('MesaiTanim').prefetch_related('mercis657_stoplar')

    # izin kaynaklı azaltım (Mesai.Izin) için toplanacak
    izin_azaltimi = Decimal('0.0')

    # bayram mesaisi için toplanacak toplam (saat)
    bayram_fazla_mesai = Decimal('0.0')
    # Toplam stop süresi (saat) bu fonksiyon boyunca toplanacak
    stop_suresi = Decimal('0.0')

    def _parse_time_to_hours(tstr):
        # "HH:MM" -> Decimal saat; "24:00" -> 24.0
        try:
            parts = tstr.split(':')
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            return Decimal(h) + (Decimal(m) / Decimal(60))
        except Exception:
            return None

    for mesai in mesailer:
        # Fiili çalışma süresine ekleme (Decimal üzerinden)
        if mesai.MesaiTanim and getattr(mesai.MesaiTanim, 'Sure', None):
            total_seconds = mesai.MesaiTanim.Sure # saat cinsinden
            hours = Decimal(str(total_seconds))
            fiili_calisma_suresi += hours
            # Eğer personelin sabit_mesaisi varsa ve mesai süesi 8 saatten fazla ise sabit_mesai.ara_dinlenme süresini düş
            if sabit_mesai and fiili_calisma_suresi > 8:
                fiili_calisma_suresi -= sabit_mesai.ara_dinlenme
        else:
            hours = Decimal('0.0')

        # STOP sürelerini düş: varsa tüm StopKaydi.Sure değerlerini topla ve fiili süreden çıkar
        stopler = list(getattr(mesai, 'mercis657_stoplar').all())
        for stop in stopler:
            try:
                stop_hours = Decimal(str(stop.Sure)) if stop.Sure is not None else Decimal('0.0')
            except Exception:
                stop_hours = Decimal('0.0')
            # azalt
            fiili_calisma_suresi -= stop_hours
            stop_suresi += stop_hours

        # Eğer Mesai üzerinde izin bilgisi varsa ve tarih hafta içi ve resmi tatil değilse
        # olası gereken süreden azaltım uygula (7h radyasyon çalışanı için, yoksa 8h)
        izin_field = getattr(mesai, 'Izin', None)
        mesai_tarih = getattr(mesai, 'MesaiDate', None)
        if izin_field and mesai_tarih:
            if mesai_tarih.weekday() < 5:  # hafta içi
                is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=mesai_tarih).exists()
                if not is_resmi_tatil:
                    per_day = Decimal('7.0') if radyasyon_calisani else Decimal('8.0')
                    izin_azaltimi += per_day

        # ---- Bayram mesaisi hesaplama ----
        # MesaiTanim.Saat: "HH:MM HH:MM" -> öncesi = baslangic, sonrası = bitis
        if mesai.MesaiTanim and getattr(mesai.MesaiTanim, 'Saat', None) and mesai_tarih:
            saat_str = mesai.MesaiTanim.Saat.strip()
            parts = saat_str.split()
            if len(parts) >= 2:
                bas_str = parts[0]
                bit_str = parts[1]
                bas_saat = _parse_time_to_hours(bas_str)
                bit_saat = _parse_time_to_hours(bit_str)
                if bas_saat is not None and bit_saat is not None:
                    # Arefe kontrolü
                    is_arefe = ResmiTatil.objects.filter(TatilTarihi=mesai_tarih, ArefeMi=True).exists()
                    is_resmi = ResmiTatil.objects.filter(TatilTarihi=mesai_tarih).exists()

                    if is_arefe:
                        # Arefede 13:00 sonrası bayram mesaisi
                        limit = Decimal('13.0')
                        if bit_saat > limit:
                            bayram_part = bit_saat - limit
                        else:
                            bayram_part = (bit_saat + Decimal('24.0')) - limit
                        if bayram_part > 0:
                            bayram_fazla_mesai += bayram_part
                    elif is_resmi:
                        # Bayram günü
                        next_day = mesai_tarih + timedelta(days=1)
                        next_is_resmi = ResmiTatil.objects.filter(TatilTarihi=next_day).exists()
                        if next_is_resmi:
                            # tüm çalışma bayram mesaisi
                            bayram_fazla_mesai += hours
                        else:
                            # bayramın son günü: 24:00'e kadar olan kısım bayram mesaisi
                            sonraki_sarkiyor = getattr(mesai.MesaiTanim, 'SonrakiGuneSarkiyor', False)
                            if sonraki_sarkiyor:
                                part = Decimal('24.0') - bas_saat
                                if part > 0:
                                    bayram_fazla_mesai += part
                            else:
                                end_for_bayram = bit_saat if bit_saat <= Decimal('24.0') else Decimal('24.0')
                                part = end_for_bayram - bas_saat
                                if part > 0:
                                    bayram_fazla_mesai += part
        # ---- /Bayram mesaisi hesaplama ----

    # Mazeret azaltımını hesapla
    mazeret_azaltimi = Decimal('0.0')
    mazeret_kayitlari = MazeretKaydi.objects.filter(
        personel=personel,
        baslangic_tarihi__lte=date(year, month, days_in_month),
        bitis_tarihi__gte=date(year, month, 1)
    )

    for mazeret in mazeret_kayitlari:
        # Mazeret dönemindeki çalışma günlerini hesapla
        baslangic = max(mazeret.baslangic_tarihi, date(year, month, 1))
        bitis = min(mazeret.bitis_tarihi, date(year, month, days_in_month))

        mazeret_gunleri = 0
        current_date = baslangic
        while current_date <= bitis:
            if current_date.weekday() < 5:  # Hafta içi
                # Resmi tatil değilse say
                is_resmi_tatil = resmi_tatiller.filter(TatilTarihi=current_date).exists()
                if not is_resmi_tatil:
                    mazeret_gunleri += 1
            current_date += timedelta(days=1)

        mazeret_azaltimi += mazeret_gunleri * mazeret.gunluk_azaltim_saat

    # Mevcut kabul edilen davranış: mazeret azaltımı fiili çalışma süresine ekleniyor
    fiili_calisma_suresi += mazeret_azaltimi

    # İzin azaltımını olması gereken süreden düş
    olmasi_gereken_sure -= izin_azaltimi

    # Fazla mesai hesapla
    fazla_mesai = fiili_calisma_suresi - olmasi_gereken_sure

    # Bayram/normal ayrımı kuralları
    normal_fazla_mesai = Decimal('0.0')
    bayram_fazla = bayram_fazla_mesai
    if fazla_mesai <= Decimal('0.0'):
        bayram_fazla = Decimal('0.0')
        normal_fazla_mesai = Decimal('0.0')
    else:
        if bayram_fazla > Decimal('0.0'):
            if bayram_fazla < fazla_mesai:
                normal_fazla_mesai = fazla_mesai - bayram_fazla
            else:
                bayram_fazla = fazla_mesai
                normal_fazla_mesai = Decimal('0.0')
        else:
            normal_fazla_mesai = fazla_mesai

    return {
        'olması_gereken_sure': olmasi_gereken_sure,
        'fiili_calisma_suresi': fiili_calisma_suresi,
        'fazla_mesai': fazla_mesai,
        'calisma_gunleri': calisma_gunleri,
        'arefe_gunleri': arefe_gunleri,
        'mazeret_azaltimi': mazeret_azaltimi,
        'bayram_fazla_mesai': bayram_fazla_mesai,
        'normal_fazla_mesai': normal_fazla_mesai,
        'stop_suresi': stop_suresi
    }

def get_favori_mesailer(user):
    """Kullanıcının favori mesailerini döndürür. Favori yoksa tüm mesailer gelir."""
    favoriler = UserMesaiFavori.objects.filter(user=user).select_related("mesai").order_by("mesai")
    if favoriler.exists():
        return [f.mesai for f in favoriler]
    return Mesai_Tanimlari.objects.all().order_by("Saat")
