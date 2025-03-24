# RFC-003: Mesai ve İcap Bildirimi Modülü

## Özet
Bu RFC, çalışma çizelgelerinden elde edilen verilerin fazla mesai ve icap nöbeti bildirimlerinin yönetimini tanımlar.

## Motivasyon
- Personelin fazla mesai ve icap nöbetlerinin resmi olarak kayıt altına alınması
- Birim bazlı onay mekanizmasının oluşturulması
- Verilerin raporlama için hazırlanması

## Veri Modeli

### Bildirim Tablosu
```python
class Bildirim:
    BildirimID = models.AutoField(primary_key=True)
    PersonelID = models.ForeignKey('Personel')
    BirimID = models.ForeignKey('Birim')
    DonemBaslangic = models.DateField()  # Ay başı tarihi
    BildirimTipi = models.CharField(choices=['MESAI', 'ICAP'])
    
    # Mesai süreleri (saat cinsinden)
    NormalFazlaMesai = models.IntegerField(default=0)
    BayramFazlaMesai = models.IntegerField(default=0)
    RiskliNormalFazlaMesai = models.IntegerField(default=0)
    RiskliBayramFazlaMesai = models.IntegerField(default=0)
    
    # İcap süreleri
    NormalIcap = models.IntegerField(default=0)
    BayramIcap = models.IntegerField(default=0)
    
    # Günlük kayıtlar (JSON)
    MesaiDetay = models.JSONField()  # {date: hours}
    IcapDetay = models.JSONField()   # {date: hours}
    
    # İşlem bilgileri
    OlusturanKullanici = models.ForeignKey('User')
    OlusturmaTarihi = models.DateTimeField(auto_now_add=True)
    OnaylayanKullanici = models.ForeignKey('User', null=True)
    OnayTarihi = models.DateTimeField(null=True)
    OnayDurumu = models.IntegerField(default=0)  # 0: Bekliyor, 1: Onaylandı
    SilindiMi = models.BooleanField(default=False)
```

## API Endpoints

### Bildirim İşlemleri
```python
# Bildirim CRUD
POST /api/bildirim/olustur/{tip}/
GET /api/bildirim/liste/{donem}/{birim_id}/
PUT /api/bildirim/guncelle/{bildirim_id}/
DELETE /api/bildirim/sil/{bildirim_id}/

# Toplu işlemler
POST /api/bildirim/toplu-olustur/{birim_id}/
POST /api/bildirim/toplu-onay/{birim_id}/
```

## Frontend Bileşenleri

### 1. Üst Kontrol Paneli
```html
<div class="control-panel">
    <!-- Dönem ve Birim Seçimi -->
    <select id="selectYear">...</select>
    <select id="selectMonth">...</select>
    <select id="selectBirim">...</select>
    
    <!-- Mod Değiştirme -->
    <button id="toggleMode">İcap/Mesai Modu</button>
    
    <!-- İşlem Butonları -->
    <button id="createAllNotifications">Tüm Personele Bildirim</button>
    <button id="downloadForm">Bildirim Formu</button>
</div>
```

### 2. Tablo Yapısı
```html
<!-- Mesai Bildirimi Tablosu -->
<table id="mesaiBildirimTable">
    <thead>
        <tr>
            <th>Sıra</th>
            <th>Personel</th>
            <th>Normal Mesai</th>
            <th>Bayram Mesai</th>
            <th>Riskli Normal</th>
            <th>Riskli Bayram</th>
            {% for day in month_days %}
            <th class="{{ day.type }}">{{ day.num }}</th>
            {% endfor %}
        </tr>
    </thead>
</table>

<!-- İcap Bildirimi Tablosu -->
<table id="icapBildirimTable" style="display:none">
    <thead>
        <tr>
            <th>Sıra</th>
            <th>Personel</th>
            <th>Normal İcap</th>
            <th>Bayram İcap</th>
            {% for day in month_days %}
            <th class="{{ day.type }}">{{ day.num }}</th>
            {% endfor %}
        </tr>
    </thead>
</table>
```

## Hesaplama Metodları

### Fazla Mesai Hesaplama
```python
def hesapla_fazla_mesai(personel_id, baslangic_tarih, bitis_tarih):
    mesailer = Mesai.objects.filter(
        Personel_id=personel_id,
        MesaiDate__range=(baslangic_tarih, bitis_tarih)
    )
    
    sonuc = {
        'normal': 0,
        'bayram': 0,
        'riskli_normal': 0,
        'riskli_bayram': 0,
        'gunluk_detay': {}
    }
    
    for mesai in mesailer:
        # Standart çalışmayı al (birden fazlaysa ilkini)
        standart = mesai.Hizmetler.filter(
            HizmetTipi='Standart'
        ).first()
        
        # Nöbet çalışmasını al
        nobet = mesai.Hizmetler.filter(
            HizmetTipi='Nöbet'
        ).first()
        
        # Toplam süreyi hesapla
        toplam = (standart.HizmetSuresi if standart else 0) + 
                (nobet.HizmetSuresi if nobet else 0)
        
        sonuc['gunluk_detay'][mesai.MesaiDate] = toplam
        
        if mesai.is_bayram:
            sonuc['bayram' if not mesai.is_riskli else 'riskli_bayram'] += toplam
        else:
            sonuc['normal' if not mesai.is_riskli else 'riskli_normal'] += toplam
            
    return sonuc
```

## Onay Süreci
1. Bildirimin oluşturulması
2. Yetkili kullanıcı onayına sunulması
3. Onay/red işlemi
4. Bildirim formunun oluşturulması

## Kabul Kriterleri
1. İki farklı bildirim tipi (Mesai/İcap) yönetilebilmeli
2. Günlük çalışma detayları saklanmalı
3. Birim bazlı toplu bildirim oluşturulabilmeli
4. Onay süreci takip edilebilmeli
5. Bildirim formları çıktı alınabilmeli

## İleri Aşama Geliştirmeler
1. Otomatik bildirim oluşturma
2. E-imza entegrasyonu
3. Personel onay/red bildirimleri
4. Raporlama modülü entegrasyonu
