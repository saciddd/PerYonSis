# RFC-002: Mesai Kontrol Mekanizmaları

## Özet
Bu RFC, çizelge sistemindeki kontrol mekanizmalarının detaylarını ve implementasyonunu tanımlar.

## Motivasyon
Hatalı çizelge girişlerinin önlenmesi ve yasal düzenlemelere uygunluğun sağlanması.

## Kontrol Kategorileri

### 1. Zaman Bazlı Kontroller
```python
class MesaiKontrol:
    def gunluk_mesai_kontrol(personel_id, tarih):
        """Günlük maksimum çalışma süresi kontrolü"""
        max_sure = 24 * 60  # 24 saat
        return toplam_sure <= max_sure

    def haftalik_dinlenme_kontrol(personel_id, tarih):
        """Haftalık zorunlu dinlenme kontrolü"""
        min_dinlenme = 24 * 60  # 24 saat
        return dinlenme_suresi >= min_dinlenme

    def aylik_nobet_kontrol(personel_id, yil, ay):
        """Aylık maksimum nöbet sayısı kontrolü"""
        max_nobet = 10
        return nobet_sayisi <= max_nobet
```

### 2. Hizmet Bazlı Kontroller
```python
class HizmetKontrol:
    def cakisma_kontrol(personel_id, tarih, yeni_hizmet):
        """Aynı gün içinde çakışan hizmet kontrolü"""
        mevcut_hizmetler = get_personel_hizmetler(personel_id, tarih)
        return not any(cakisan for cakisan in mevcut_hizmetler)

    def yetkinlik_kontrol(personel_id, hizmet_id):
        """Personelin hizmet için yetkinlik kontrolü"""
        return personel_yetkinlikleri.contains(hizmet_id)
```

### 3. Hizmet Kombinasyon Kontrolleri
```python
def validate_hizmet_combination(hizmetler):
    """Hizmet kombinasyonlarının geçerliliğini kontrol eder"""
    errors = []
    
    # Standart hizmet sayısı kontrolü (varsayılan + max 1)
    standart_hizmetler = [h for h in hizmetler if h.HizmetTipi == 'Standart']
    if len(standart_hizmetler) > 2:
        errors.append("En fazla 2 standart hizmet tanımlanabilir")

    # Nöbet ve İcap kontrolü
    nobet_hizmetler = [h for h in hizmetler if h.HizmetTipi == 'Nöbet']
    icap_hizmetler = [h for h in hizmetler if h.HizmetTipi == 'İcap']
    
    if nobet_hizmetler and icap_hizmetler:
        errors.append("Nöbet ve İcap hizmetleri aynı güne tanımlanamaz")
        
    return not errors, errors
```

## Onay Süreci
1. Mesai Girişi -> İlk Kontrol
2. İdare Onayı
3. Değişikliklerin Takibi
4. Değişikliklerin İdare Onayı

## Hata Yönetimi
- Validasyon hataları
- İş kuralı ihlalleri
- Çakışma kayıtları
- Onay geçmişi

## Kabul Kriterleri
1. Tüm çakışmalar gerçek zamanlı tespit edilmeli
2. Kullanıcıya anlaşılır hata mesajları gösterilmeli
3. Kritik hataların kaydı tutulmalı

## Risk Analizi
- Performans etkileri
- Yanlış pozitif/negatif kontroller
- Sistem karmaşıklığı

## İlgili Belgeler
- 657 sayılı DMK Çalışma koşulları
- Hastane iç yönetmelikleri
