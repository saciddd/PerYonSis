# RFC-009 - Icap Bildirimleri

Mercis657 sistemine personellerin icap çalışmalarını cizelgelerine işlemek ve bu veriler üzerinden bildirimlerin oluşturulmasını sağlamak için uygulamada gerekli değişiklikler yapılacaktır.

Mesai modeline Icap alanı eklenecek. Bool tipinde olacak.

## İcap hesaplaması:

1. İcap personelin mesaiden sonra acil durumlarda göreve gelecek şekilde hazır bulunması demektir. Bu nedenle hesaplama yaparken mesai sonrasındaki süreleri hesaba katacağız.
2. Eğer mesai.MesaiTanim varsa bu mesainin bittiği saatten bir sonraki gün saat 08:00 a kadar olan süre o günkü icap olarak hesaplanacak.
3. Eğer mesai.MesaiTanim yoksa icap süresi direkt 24 saat olarak hesaplanacak.
4. İcap çalışmalarının bayram dönemine denk gelen kısmı bayram icap olarak hesaplanacak.
5. aşağıda daha önce kullandığımız örnek bir hesaplama fonksiyonu bulunmaktadır. Bu fonksiyonu mevcut sisteme uyarlayarak kullanacağız.
Not: İcap çalışmasında riskli - risksiz ayrımı bulunmayacak.

## Değişiklik yapılacak sayfalar şunlardır:

1. cizelge.html
2. bildirimler.html

# cizelge.html sayfasındaki değişiklikler:

1. Alanı boşalt ve stoplama modu switch'lerinin altına İcap Girişi switch'ini ekle. Bu switch ve metin yeşil olmalı.
2. İcap Girişi switch'ini aktif edilirse tıklanan hücredeki mesai kaydının Icap alanı true olarak kaydedilecek. Eğer zaten true ise false olarak kaydedilecek.
3. İcap switchi diğer switch'leri kapatacak. Diğer switch'ler aktif edilirse İcap switchi kapatacak.
4. İzinli güne icap girilemez. Bu nedenle eğer mesai.Izin != null ise o güne icap girişi yapılmaz.
5. İcap = True olan hücreler belli olacak biçimde gösterilecek. İcon konabilir veya renkli olabilir. Sayfanın üst bölümünde açıklama ile belirtilecek.
6. Fazla Mesai sütunu Fazla Mesai/İcap olarak değiştirilecek.
7. Sütundaki İcap verileri gri renkte gösterilecek.

# bildirimler.html sayfasındaki değişiklikler:

1. Sayfada icap verileri için gerekli alanlar zaten mevcut.
2. bildirim_views.py dosyasındaki def bildirim_olustur(request): fonksiyonunun icap bildirimlerini de içerdiğinden emin ol. Bu veriler bildirimler.html sayfasına aktarılacak.

# Kullandığımız eski icap hesaplama fonksiyonu:

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