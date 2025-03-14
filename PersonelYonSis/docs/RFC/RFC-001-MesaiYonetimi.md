# RFC-001: Mesai Yönetimi

## Özet
Hastane personelinin mesai, nöbet ve icap görevlerinin yönetimi.

## Mevcut Veri Modeli
```python
class Mesai:
    MesaiID: int
    Personel: ForeignKey(Personel)
    MesaiDate: date
    Hizmetler: ManyToManyField(Hizmet)  # Günlük hizmetler

class Hizmet:
    HizmetID: int
    HizmetName: str
    HizmetTipi: str  # (Standart, Nöbet, İcap)
    HizmetSuresi: DurationField
```

## Yeni Özellikler

### 1. Onay Mekanizması
```python
class MesaiOnay:
    OnayID: int
    Mesai: ForeignKey(Mesai)
    OnayDurumu: int  # (0: Bekliyor, 1: Onaylandı, 2: Reddedildi)
    OnayTarihi: datetime
    Onaylayan: ForeignKey(User)
    Aciklama: str
```

### 2. Hizmet Çakışma Kontrolleri
```python
class HizmetCakisma:
    Hizmet1: ForeignKey(Hizmet)
    Hizmet2: ForeignKey(Hizmet)
    CakismaTipi: str  # (Tam, Kısmi, İzinli)
```

### 3. API Endpoints
```python
# Mesai Onay İşlemleri
POST /api/mesai/onay/{mesai_id}/
GET /api/mesai/onay-durumu/{mesai_id}/

# Raporlama
GET /api/rapor/personel/{personel_id}/{yil}/{ay}/
GET /api/rapor/birim/{birim_id}/{yil}/{ay}/
GET /api/rapor/nobet-sayilari/{personel_id}/{yil}/
```

## Temel Özellikler
1. Mesai Kaydı
   - Günlük mesai girişi
   - Toplu mesai girişi
   - Çakışma kontrolü

2. Raporlama
   - Günlük mesai listesi
   - Gün bazlı haftalık çalışma listesi
   - Aylık mesai özeti
   - Personel nöbet istatistikleri
   - Personel icap istatistikleri
   - Fazla mesai hesaplamaları

3. Kontroller
   - Yasal çalışma süreleri
   - Hizmet çakışmaları
   - Nöbet süreleri
   - İcap nöbetleri

## İlişkili Tablolar
- Personel
- Birim
- Hizmet
- Mesai

## Örnek Sorgular
```sql
-- Bir personelin aylık mesai özeti
SELECT 
    m.MesaiDate,
    GROUP_CONCAT(h.HizmetName) as Hizmetler,
    SUM(mt.HizmetSuresi) as ToplamSure
FROM 
    Mesai m
    JOIN Hizmet h ON m.HizmetID = h.HizmetID
WHERE 
    m.PersonelID = ? 
    AND YEAR(m.MesaiDate) = ? 
    AND MONTH(m.MesaiDate) = ?
GROUP BY 
    m.MesaiDate;
```
