from datetime import date, timedelta
from decimal import Decimal
import calendar
from .models import ResmiTatil, MazeretKaydi, Mesai, Mesai_Tanimlari


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
        }
    """
    personel = personel_listesi_kayit.personel
    radyasyon_calisani = personel_listesi_kayit.radyasyon_calisani
    
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
    arefe_ekleme = arefe_gunleri * Decimal('5.0')
    olmasi_gereken_sure = normal_calisma_suresi + arefe_ekleme
    
    # Fiili çalışma süresini hesapla
    fiili_calisma_suresi = Decimal('0.0')
    
    # O ayki mesai kayıtlarını al
    mesailer = Mesai.objects.filter(
        Personel=personel,
        MesaiDate__year=year,
        MesaiDate__month=month,
        OnayDurumu=True  # Sadece onaylı mesailer
    ).select_related('MesaiTanim')
    
    for mesai in mesailer:
        if mesai.MesaiTanim and mesai.MesaiTanim.Sure:
            # Sure DurationField'dan saat cinsine çevir
            total_seconds = mesai.MesaiTanim.Sure.total_seconds()
            hours = Decimal(str(total_seconds / 3600))
            fiili_calisma_suresi += hours
    
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
    
    # Fiili çalışma süresinden mazeret azaltımını çıkar
    fiili_calisma_suresi -= mazeret_azaltimi
    
    # Fazla mesai hesapla
    fazla_mesai = fiili_calisma_suresi - olmasi_gereken_sure
    
    return {
        'olması_gereken_sure': olmasi_gereken_sure,
        'fiili_calisma_suresi': fiili_calisma_suresi,
        'fazla_mesai': fazla_mesai,
        'calisma_gunleri': calisma_gunleri,
        'arefe_gunleri': arefe_gunleri,
        'mazeret_azaltimi': mazeret_azaltimi
    }
