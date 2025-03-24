# Hekim Çizelge Modülü

## Genel Açıklama
Hekim Çizelge modülü, hastanedeki hekim personelinin çalışma çizelgelerini yönetmek için geliştirilmiştir. Temel özellikleri:
- Aylık çalışma çizelgelerinin oluşturulması
- Standart mesai, nöbet ve icap hizmetlerinin planlanması
- İzin takibi
- Onay mekanizması
- Çakışma kontrolleri

## Model Yapısı

### Birim
- Hastane içindeki bölümleri temsil eder
- Her birimin varsayılan bir hizmeti ve ek hizmetleri vardır
- Birim-personel ilişkisi PersonelBirim modeli üzerinden yönetilir

### Personel
- Hekim bilgilerini tutar
- Birimlerle many-to-many ilişkisi vardır
- Ad, unvan ve branş bilgileri içerir

### Hizmet
- Personelin yapabileceği görevleri tanımlar
- Tipler: Standart, Nöbet, İcap
- Her hizmet için süre ve maksimum hekim sayısı belirlenebilir
- Nöbet sonrası izin durumu ayarlanabilir

### Mesai
- Personel-tarih bazlı çalışma kayıtlarını tutar
- Birden fazla hizmet içerebilir
- İzin kaydı tutulabilir
- Onay durumu takip edilir

### İzin
- İzin tiplerini tanımlar (Yıllık, Nöbet, İdari vb.)
- Her izin tipi için renk tanımı içerir

## Önemli Fonksiyonlar

### views.py
- `cizelge()`: Ana çizelge görünümünü oluşturur
- `cizelge_kaydet()`: Çizelge değişikliklerini kaydeder
- `auto_fill_default()`: Boş günlere varsayılan hizmet atar
- `mesai_onay()`: Mesai onay işlemlerini yönetir

### models.py > MesaiKontrol
- `validate_hizmet_combination()`: Hizmet kombinasyonlarının geçerliliğini kontrol eder
- `nobet_ertesi_kontrol()`: Nöbet sonrası mesai kontrolü yapar
- `mesai_sure_hesapla()`: Günlük mesai sürelerini hesaplar

## Kontrol Mekanizmaları

### Hizmet Kombinasyonu Kuralları
1. Varsayılan + max 1 standart hizmet
2. Max 1 nöbet veya 1 icap hizmeti
3. Nöbet ve icap aynı güne gelemez

### Zaman Kontrolleri
1. Nöbet sonrası mesai kontrolü
2. Hafta içi/sonu ayrımı
3. Günlük maksimum çalışma süresi kontrolü

### Onay Süreci
1. Değişiklikler önce onaylanmamış olarak kaydedilir
2. Yetkili kullanıcı onaylar/reddeder
3. Onaylı kayıtlar değiştirilemez

## Planlanan İşler

### Yakın Dönem
- [ ] Mesai süresi hesaplama ve raporlama
- [ ] İzin bakiye takibi
- [ ] Hizmet çakışma kontrollerinin iyileştirilmesi

### Orta Dönem
- [ ] Mobil görünüm optimizasyonu
- [ ] Otomatik çizelge önerisi
- [ ] E-posta bildirimleri

### Uzun Dönem
- [ ] Yapay zeka destekli planlama
- [ ] Personel tercih sistemi
- [ ] İleri düzey raporlama

## Önemli Değişiklikler

### v1.1
- Çoklu hizmet desteği eklendi
- Mesai kaydetme fonksiyonu güncellendi
- Hizmet kombinasyon kontrolleri eklendi

### v1.0
- Temel CRUD işlemleri
- Basit onay mekanizması
- Tekli hizmet desteği
