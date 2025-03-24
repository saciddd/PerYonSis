# RFC-001: Çizelge Yönetimi Temel Özellikleri

## Özet
Bu RFC, çizelge yönetimi modülünün temel özelliklerini ve implementasyon detaylarını tanımlar.

## Motivasyon
Hastane personelinin çalışma çizelgelerinin etkin yönetimi için kullanıcı dostu bir arayüz ve güvenilir bir altyapı gerekmektedir.

## Tasarım Detayları

### 1. Çizelge Görünümleri
- Aylık takvim görünümü
- Hekim bazlı görünüm
- Hizmet bazlı görünüm
- Görünümler arası geçiş özelliği

### 2. Veri Yapısı
```python
class Cizelge:
    birim_id: int
    yil: int
    ay: int
    personel_id: int
    tarih: date
    hizmetler: List[int]
    varsayilan_hizmet: int
    olusturan: int
    olusturma_tarihi: datetime
    duzenleyen: int
    duzenleme_tarihi: datetime
    onay_durumu: int
```

### 3. API Endpoints
```python
# Çizelge CRUD işlemleri
GET /api/cizelge/{yil}/{ay}/{birim_id}/
POST /api/cizelge/kaydet/
PUT /api/cizelge/guncelle/{id}/
DELETE /api/cizelge/sil/{id}/

# Toplu işlemler
POST /api/cizelge/toplu-kayit/
POST /api/cizelge/kopyala/{kaynak_ay}/{hedef_ay}/
```

### 4. Temel İşlevler
- Çizelge oluşturma ve düzenleme
- Varsayılan hizmet tanımlama
- Çakışma kontrolü
- Toplu güncelleme
- Çizelge kopyalama
- Onay akışı yönetimi

## Hizmet Kombinasyon Kuralları
- Varsayılan hizmet + max 1 ek standart hizmet
- Maximum 1 nöbet veya 1 icap hizmeti 
- Nöbet ve icap hizmetleri aynı güne tanımlanamaz

### Veri Modeli Güncellemesi
```python
class Mesai:
    # ...existing fields...
    Hizmetler = models.ManyToManyField('Hizmet')  # Çoklu hizmet desteği
    Izin = models.ForeignKey('Izin', null=True)   # İzin kaydı
    Degisiklik = models.BooleanField(default=True) # Onay takibi için
```

## Kabul Kriterleri
1. Kullanıcılar aylık çizelge oluşturabilmeli
2. Farklı görünümler arasında geçiş yapabilmeli
3. Çakışma kontrolleri otomatik yapılmalı
4. Değişiklikler anlık kaydedilebilmeli
5. Onay süreci başlatılabilmeli

## Risk Analizi
- Veri tutarlılığı
- Performans etkileri
- Kullanıcı hatalarının önlenmesi

## Implementasyon Planı
1. Veritabanı şeması oluşturma
2. API katmanı geliştirme
3. Frontend komponentleri geliştirme
4. Test süreçleri
5. Dokümantasyon

## Geliştirme Takvimi
- Tasarım ve Planlama: 1 hafta
- Backend Geliştirme: 2 hafta
- Frontend Geliştirme: 2 hafta
- Test ve Optimizasyon: 1 hafta
