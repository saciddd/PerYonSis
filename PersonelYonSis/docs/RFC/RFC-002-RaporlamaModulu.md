# RFC-002: Raporlama Modülü

## Özet
Mesai ve nöbet verilerinin raporlanması için gerekli modül.

## Rapor Türleri

### 1. Personel Bazlı Raporlar
- Aylık mesai özeti
- Nöbet sayıları (aylık/yıllık)
- İcap nöbeti sayıları
- Fazla mesai süreleri

### 2. Birim Bazlı Raporlar
- Günlük çalışma listesi
- Haftalık nöbet çizelgesi
- Aylık mesai dağılımı

### 3. Yönetim Raporları
- Onay bekleyen mesailer
- Birim bazlı istatistikler
- Personel performans özeti

## API Endpoints
```python
# Personel Raporları
GET /api/rapor/personel/mesai/{personel_id}/{yil}/{ay}/
GET /api/rapor/personel/nobet/{personel_id}/{yil}/{ay}/
GET /api/rapor/personel/icap/{personel_id}/{yil}/{ay}/

# Birim Raporları
GET /api/rapor/birim/gunluk/{birim_id}/{tarih}/
GET /api/rapor/birim/haftalik/{birim_id}/{hafta}/
GET /api/rapor/birim/aylik/{birim_id}/{yil}/{ay}/

# Yönetim Raporları
GET /api/rapor/yonetim/onay-bekleyen/
GET /api/rapor/yonetim/birim-ozet/{yil}/{ay}/
```

## Örnek Rapor Sorguları
```sql
-- Personel aylık nöbet sayısı
SELECT 
    COUNT(*) as NobetSayisi,
    h.HizmetTipi
FROM Mesai m
JOIN Hizmet h ON h.HizmetID IN (
    SELECT HizmetID FROM mesai_hizmetler 
    WHERE mesai_id = m.MesaiID
)
WHERE 
    m.Personel_id = ? AND 
    YEAR(m.MesaiDate) = ? AND 
    MONTH(m.MesaiDate) = ? AND
    h.HizmetTipi = 'Nöbet'
GROUP BY h.HizmetTipi;
```
