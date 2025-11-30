# RFC-006: Çizelge Mesai Kontrolü ve Anlık Hesaplama Özellikleri

## Özet
Bu RFC, mercis657 uygulamasındaki çizelge sayfasına üç yeni özellik eklenmesini tanımlar:
1. Anlık fazla mesai hesaplama
2. Vardiya sayıları gösterimi
3. Liste kontrolü (hata tespiti)

## Motivasyon
Çizelge sayfasında kullanıcıların mesai verilerini girerken anlık olarak fazla mesai durumunu görmesi, vardiya dağılımını takip etmesi ve hataları tespit etmesi gerekmektedir. Bu özellikler sayesinde kullanıcılar daha verimli çalışabilecek ve hataları erken tespit edebilecektir.

## Tasarım Detayları

### 1. Anlık Fazla Mesai Hesaplama

#### 1.1. Genel Yaklaşım
- Sayfa yüklendiğinde mevcut kaydedilmiş veriler üzerinden bir kez hesaplama yapılacak
- Kullanıcı mesai hücresine tıkladığında veya mesai verisi değiştiğinde hafif bir JavaScript fonksiyonu çalışarak sadece ilgili personelin fazla mesai değerini güncelleyecek
- JavaScript fonksiyonu ayrı bir dosyada (`static/mercis657/js/fazla_mesai_hesapla.js`) yazılacak

#### 1.2. Backend Fonksiyonu (Sadeleştirilmiş)
Mevcut `hesapla_fazla_mesai` fonksiyonundan türetilecek yeni bir fonksiyon:
- **İsim**: `hesapla_fazla_mesai_sade`
- **Parametreler**: 
  - `personel_id`: int
  - `year`: int
  - `month`: int
  - `mesai_data`: dict (opsiyonel, kaydedilmemiş veriler için)
- **Döndürdüğü**: Sadece `fazla_mesai` değeri (Decimal)
- **Özellikler**:
  - Bayram mesaisi hesaplaması yapılmayacak (sadeleştirme)
  - Temel hesaplama mantığı korunacak:
    - Olması gereken süre hesaplama (çalışma günleri × günlük saat + arefe artırımı)
    - Fiili çalışma süresi hesaplama (mesai süreleri toplamı - stop süreleri + mazeret azaltımı)
    - İzin azaltımı
    - Mazeret azaltımı
    - Stop süreleri

#### 1.3. JavaScript Implementasyonu

**Dosya**: `static/mercis657/js/fazla_mesai_hesapla.js`

**Fonksiyonlar**:
1. `calculateFazlaMesaiForPersonel(personelId, year, month)`
   - Backend'e AJAX isteği gönderir
   - Sadece ilgili personelin fazla mesai değerini günceller
   - DOM'da `.fazla-mesai-cell` içindeki değeri günceller

2. `updateFazlaMesaiOnCellChange(cell)`
   - Hücre değiştiğinde çağrılır
   - İlgili personel ID'sini alır
   - `calculateFazlaMesaiForPersonel` fonksiyonunu çağırır

3. `initializeFazlaMesaiCalculation()`
   - Sayfa yüklendiğinde çağrılır
   - Tüm personeller için fazla mesai hesaplar
   - Backend'den toplu veri alabilir veya her personel için ayrı istek yapabilir

**Event Listener'lar**:
- `.mesai-cell` üzerinde `click` veya `change` eventi
- Mesai hücresi değiştiğinde ilgili personelin fazla mesai değerini güncelle

**Backend Endpoint**:
```
GET /mercis657/fazla-mesai-hesapla-anlik/?personel_id={id}&year={year}&month={month}
```
veya toplu:
```
POST /mercis657/fazla-mesai-hesapla-toplu/
Body: { personel_ids: [1,2,3], year: 2024, month: 1 }
```

#### 1.4. Performans Optimizasyonu
- Debounce mekanizması: Kullanıcı hızlı değişiklik yapıyorsa, son değişiklikten sonra 500ms bekleyip hesaplama yap
- Toplu hesaplama: Sayfa yüklendiğinde tüm personeller için tek bir istek
- Cache mekanizması: Aynı personel için kısa süre içinde tekrar hesaplama yapma

---

### 2. Vardiya Sayıları Gösterimi

#### 2.1. UI Tasarımı
Tablonun üst kısmında (thead içinde), günlerin gösterildiği satırın üstüne 3 yeni satır eklenecek:
- **Gündüz Vardiyası Satırı**: Her gün için gündüz mesaisi olan personel sayısı
- **Akşam Vardiyası Satırı**: Her gün için akşam mesaisi olan personel sayısı
- **Gece Vardiyası Satırı**: Her gün için gece mesaisi olan personel sayısı

**HTML Yapısı**:
```html
<thead>
    <tr class="vardiya-row gunduz-row">
        <th colspan="4">Gündüz</th>
        <th class="vardiya-count" data-date="2024-01-01">0</th>
        <!-- Her gün için bir th -->
    </tr>
    <tr class="vardiya-row aksam-row">
        <th colspan="4">Akşam</th>
        <th class="vardiya-count" data-date="2024-01-01">0</th>
    </tr>
    <tr class="vardiya-row gece-row">
        <th colspan="4">Gece</th>
        <th class="vardiya-count" data-date="2024-01-01">0</th>
    </tr>
    <tr>
        <!-- Mevcut günler satırı -->
    </tr>
</thead>
```

#### 2.2. Vardiya Belirleme Mantığı
`Mesai_Tanimlari` modelinde:
- `GunduzMesaisi`: Boolean
- `AksamMesaisi`: Boolean
- `GeceMesaisi`: Boolean

Her mesai tanımı için bu alanlardan biri `True` olmalı. Bir mesai tanımı birden fazla vardiyaya ait olabilir (örneğin hem gündüz hem akşam).

**Hesaplama Mantığı**:
- Her gün için, o günde mesai tanımı olan tüm personelleri tara
- Her personelin mesai tanımının vardiya tipini kontrol et
- İlgili vardiya sayacını artır

#### 2.3. JavaScript Implementasyonu

**Dosya**: `static/mercis657/js/vardiya_sayilari.js`

**Fonksiyonlar**:
1. `calculateVardiyaCounts()`
   - Tüm günler için vardiya sayılarını hesaplar
   - DOM'u günceller

2. `updateVardiyaCountForDay(date)`
   - Belirli bir gün için vardiya sayılarını günceller
   - Mesai hücresi değiştiğinde çağrılır

3. `getVardiyaType(mesaiTanimId)`
   - Mesai tanımının vardiya tipini döndürür
   - Backend'den veya sayfa yüklendiğinde alınan verilerden

**Backend Endpoint** (opsiyonel):
```
GET /mercis657/vardiya-tanimlari/
Response: { mesai_tanimlari: { id: { gunduz: bool, aksam: bool, gece: bool } } }
```

#### 2.4. Anlık Güncelleme
- Mesai hücresine tıklandığında veya değiştiğinde, ilgili günün vardiya sayıları güncellenir
- Kaydet butonuna basıldığında tüm vardiya sayıları yeniden hesaplanır

---

### 3. Liste Kontrolü (Hata Tespiti)

#### 3.1. Genel Yaklaşım
"Hata Kontrolü" butonu zaten mevcut. Bu butona basıldığında veya sayfa kaydedildiğinde çeşitli kurallara göre hata kontrolü yapılacak.

**Kontrol Zamanlaması**:
- **Seçenek 1**: Sadece "Hata Kontrolü" butonuna basıldığında (önerilen)
- **Seçenek 2**: Anlık kontrol (her hücre değiştiğinde)
- **Seçenek 3**: Her ikisi de (buton + anlık)

#### 3.2. Kontrol Kuralları

##### 3.2.1. 24 Saatlik Mesai Sonrası Kontrolü
- **Kural**: 24 saatlik mesainin sonrasındaki gün mesai olmamalı
- **Mantık**:
  - Bir günde mesai tanımı `SonrakiGuneSarkiyor=True` ve süresi 24 saat veya daha fazla ise
  - Sonraki günde mesai olmamalı (izin hariç)
- **Hata Mesajı**: `"{tarih} tarihli 24 saatlik mesai sonrası {sonraki_tarih} tarihinde mesai tanımlanmamalı"`

##### 3.2.2. 5 Gün Boş Bırakılmamalı Kontrolü
- **Kural**: Personelin mesai verisi 5 gün boyunca boş bırakılmamalı
- **Mantık**:
  - Her personel için, ardışık 5 gün boyunca hiç mesai/izin verisi yoksa hata
- **Hata Mesajı**: `"{personel_adı} için {baslangic_tarih} - {bitis_tarih} arası 5 gün boyunca mesai verisi yok"`

**Not**: Önceki döneme sarkan mesailer de kontrol edilmeli. Yani ayın ilk günlerinde kontrol yapılırken, önceki ayın son günlerine de bakılmalı.

#### 3.3. JavaScript Implementasyonu

**Dosya**: `static/mercis657/js/cizelge_kontrol.js`

**Fonksiyonlar**:
1. `checkCizelgeErrors()`
   - Tüm kontrolleri çalıştırır
   - Hataları döndürür
   - Hatalı hücreleri işaretler

2. `check24HourMesaiRule()`
   - 24 saatlik mesai sonrası kontrolü

3. `check5DayEmptyRule()`
   - 5 gün boş bırakılmamalı kontrolü

4. `markErrorCells(errors)`
   - Hatalı hücreleri görsel olarak işaretler
   - Uyarı ikonları ekler

**UI Gösterimi**:
- Hatalı hücreler `.error-cell` class'ı alır
- Hücrenin sol üst köşesine uyarı ikonu (`bi-exclamation-triangle-fill`) eklenir
- İkonun üzerine gelindiğinde hata mesajı tooltip olarak gösterilir
- Hata listesi modal veya alert olarak gösterilir

**Backend Endpoint** (opsiyonel, daha güvenilir kontrol için):
```
POST /mercis657/cizelge-kontrol/
Body: { liste_id: int, year: int, month: int }
Response: { 
    errors: [
        { 
            type: str, 
            message: str, 
            personel_id: int, 
            date: str,
            cell_selector: str 
        }
    ]
}
```

#### 3.4. Önceki Döneme Sarkan Mesailer
Kontroller yapılırken, ayın ilk günlerinde önceki ayın son günlerine de bakılmalı:
- Backend'den önceki ayın son 4 gününün mesai verileri alınabilir
- Veya JavaScript tarafında önceki ayın verileri sayfa yüklendiğinde alınabilir
- Önceki dönem verileri için ayrı bir endpoint:
```
GET /mercis657/onceki-donem-mesailer/?personel_id={id}&year={year}&month={month}
```

---

## Implementasyon Adımları

### Faz 1: Anlık Fazla Mesai Hesaplama
1. Backend'de sadeleştirilmiş fazla mesai hesaplama fonksiyonu oluştur
2. Backend endpoint'i ekle (`/mercis657/fazla-mesai-hesapla-anlik/`)
3. JavaScript dosyası oluştur (`fazla_mesai_hesapla.js`)
4. Sayfa yüklendiğinde ilk hesaplamayı yap
5. Mesai hücresi değiştiğinde anlık güncelleme yap
6. Performans optimizasyonları (debounce, cache)

### Faz 2: Vardiya Sayıları
1. Backend'den mesai tanımlarının vardiya bilgilerini al (sayfa yüklendiğinde)
2. HTML'e vardiya satırlarını ekle
3. JavaScript fonksiyonlarını yaz
4. Sayfa yüklendiğinde ilk hesaplamayı yap
5. Mesai hücresi değiştiğinde anlık güncelleme yap

### Faz 3: Liste Kontrolü
1. Backend'de kontrol fonksiyonlarını yaz (opsiyonel)
2. JavaScript kontrol fonksiyonlarını yaz
3. Hata Kontrolü butonuna event listener ekle
4. Hatalı hücreleri işaretleme mekanizması
5. Hata listesi gösterimi
6. Her kontrol kuralını tek tek implemente et

---

## Teknik Detaylar

### Backend Değişiklikleri

#### Yeni Fonksiyonlar (`mercis657/utils.py`)
```python
def hesapla_fazla_mesai_sade(personel_id, year, month, mesai_data=None):
    """
    Sadeleştirilmiş fazla mesai hesaplama (bayram mesaisi hariç).
    mesai_data: Kaydedilmemiş veriler için opsiyonel dict
    """
    pass

def get_vardiya_tanimlari():
    """
    Tüm mesai tanımlarının vardiya bilgilerini döndürür.
    """
    pass

def kontrol_cizelge_hatalari(liste_id, year, month):
    """
    Çizelge hatalarını kontrol eder.
    """
    pass
```

#### Yeni View'lar (`mercis657/views/`)
```python
@login_required
def fazla_mesai_hesapla_anlik(request):
    """Anlık fazla mesai hesaplama endpoint'i"""
    pass

@login_required
def vardiya_tanimlari(request):
    """Vardiya tanımlarını döndürür"""
    pass

@login_required
def cizelge_kontrol(request):
    """Çizelge hata kontrolü endpoint'i"""
    pass
```

### Frontend Değişiklikleri

#### Yeni JavaScript Dosyaları
- `static/mercis657/js/fazla_mesai_hesapla.js`
- `static/mercis657/js/vardiya_sayilari.js`
- `static/mercis657/js/cizelge_kontrol.js`

#### HTML Değişiklikleri (`mercis657/templates/mercis657/cizelge.html`)
- Vardiya satırlarının eklenmesi
- JavaScript dosyalarının include edilmesi

---

## Test Senaryoları
Aşağıdaki senaryolar implementasyon sonrasında test ekibi tarafından kontrol edilecektir.

### Anlık Fazla Mesai
1. Sayfa yüklendiğinde fazla mesai değerlerinin görüntülendiğini kontrol et
2. Mesai hücresine tıklandığında fazla mesai değerinin güncellendiğini kontrol et
3. Mesai silindiğinde fazla mesai değerinin güncellendiğini kontrol et
4. Performans testi: 50+ personel için hızlı çalıştığını kontrol et

### Vardiya Sayıları
1. Sayfa yüklendiğinde vardiya sayılarının doğru hesaplandığını kontrol et
2. Mesai eklendiğinde vardiya sayısının arttığını kontrol et
3. Mesai silindiğinde vardiya sayısının azaldığını kontrol et
4. Birden fazla vardiyaya ait mesai tanımı için doğru sayım yapıldığını kontrol et

### Liste Kontrolü
1. 24 saatlik mesai sonrası kontrolünün çalıştığını kontrol et
2. 5 gün boş bırakılmamalı kontrolünün çalıştığını kontrol et
3. Önceki döneme sarkan mesailer için kontrolün çalıştığını kontrol et
4. Hatalı hücrelerin görsel olarak işaretlendiğini kontrol et

---

## Gelecek Geliştirmeler
- Hata kontrolleri genişletilebilir (yeni kurallar eklenebilir)
- Vardiya sayıları için renklendirme yapılabilir. (Renk Ölçekleri)
- Fazla mesai hesaplama için detaylı breakdown gösterimi eklenebilir

---

## Notlar
- Bu RFC, implementasyon sırasında detaylandırılabilir
- Bazı kontroller için backend desteği gerekebilir (özellikle önceki dönem verileri için)
- Performans optimizasyonları implementasyon sırasında yapılacak
- UI/UX iyileştirmeleri kullanıcı geri bildirimlerine göre yapılacak
