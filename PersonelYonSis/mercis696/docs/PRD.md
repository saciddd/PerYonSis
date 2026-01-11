# Mercis Local - Product Requirements Document

## 1. Ürün Özeti

### 1.1 Amaç
Mercis657, FileMaker veritabanı ile entegre çalışan, personel çizelge yönetimini lokalleştiren bir masaüstü web uygulamasıdır. Uygulama, birimlerin personel mesai planlamasını ve takibini kolaylaştırmayı hedeflemektedir.

### 1.2 Hedef Kullanıcı
- Birim yöneticileri
- İnsan kaynakları personeli
- Mesai planlama sorumluları

### 1.3 Temel Özellikler
- Kullanıcı kimlik doğrulama
- Birim bazlı personel listeleme
- Tarih aralığı bazlı çizelge görüntüleme
- Mesai/izin bilgisi güncelleme
- Toplu güncelleme işlemleri
- Değişiklik geçmişi takibi

## 2. Fonksiyonel Gereksinimler

### 2.1 Kullanıcı Girişi
- TC kimlik ve şifre ile giriş
- Yetkili olunan birimlere erişim
- Oturum yönetimi
- Güvenli çıkış

### 2.2 Çizelge Yönetimi
- 31 güne kadar tarih aralığı seçimi
- Birim bazlı personel listesi görüntüleme
- Mesai türü seçimi ve atama
- İzin türü seçimi ve atama
- Toplu güncelleme imkanı
- Değişiklik onaylama ve kaydetme

### 2.3 Veri Senkronizasyonu
- FileMaker API ile gerçek zamanlı veri alışverişi
- Değişiklik loglarının tutulması
- Hata durumlarında kullanıcı bilgilendirme

### 2.4 Raporlama
- Personel bazlı mesai özeti
- Birim bazlı mesai dağılımı
- Tarih aralığı bazlı raporlar
- İzin kullanım raporları

## 3. Teknik Gereksinimler

### 3.1 Sistem Gereksinimleri
- Python 3.8 veya üzeri
- Modern web tarayıcı
- FileMaker Server bağlantısı
- Minimum 4GB RAM
- 100MB disk alanı

### 3.2 Güvenlik Gereksinimleri
- HTTPS protokolü kullanımı
- Oturum şifreleme
- Rol bazlı yetkilendirme
- Veri şifreleme
- Güvenli dosya işlemleri

### 3.3 Performans Gereksinimleri
- Sayfa yüklenme süresi < 2 saniye
- API yanıt süresi < 1 saniye
- Eşzamanlı kullanıcı desteği
- Minimum kaynak kullanımı

## 4. UI/UX Gereksinimleri

### 4.1 Kullanıcı Arayüzü
- Modern ve temiz tasarım
- Responsive yapı
- Kolay navigasyon
- Tema desteği (Açık/Koyu)
- Erişilebilirlik standartlarına uyum

### 4.2 Kullanıcı Deneyimi
- Sezgisel kullanım
- Hızlı öğrenme eğrisi
- Klavye kısayolları
- Drag-drop desteği
- Toplu işlem kolaylığı

### 4.3 Ekran Tasarımları
1. Giriş Ekranı
   - Giriş formu
   - Hata mesajları
   
2. Ana Panel
   - Birim seçici
   - Tarih aralığı seçici
   - Personel listesi
   
3. Çizelge Ekranı
   - Mesai/İzin seçici
   - Personel tablosu
   - Kontrol butonları

## 5. Entegrasyon Gereksinimleri

### 5.1 FileMaker API
- Oturum yönetimi
- CRUD işlemleri
- Hata yönetimi
- Veri formatlama

### 5.2 Yerel Sistem
- Dosya sistemi erişimi
- Log yönetimi
- Konfigürasyon yönetimi
- Cache mekanizması

## 6. Test Gereksinimleri

### 6.1 Birim Testleri
- API fonksiyonları
- Veri işleme
- Form doğrulama

### 6.2 Entegrasyon Testleri
- FileMaker bağlantısı
- Veri senkronizasyonu
- Oturum yönetimi

### 6.3 Kullanıcı Testleri
- Arayüz kullanılabilirliği
- Performans testleri
- Yük testleri

## 7. Dağıtım ve Kurulum

### 7.1 Kurulum Gereksinimleri
- Bağımlılık yönetimi
- Konfigürasyon ayarları
- Ortam değişkenleri

### 7.2 Dokümantasyon
- Kurulum kılavuzu
- Kullanıcı kılavuzu
- API dokümantasyonu
- Hata çözüm kılavuzu

## 8. Destek ve Bakım

### 8.1 Teknik Destek
- Hata raporlama
- Çözüm süreçleri
- Güncelleme yönetimi

### 8.2 Kullanıcı Desteği
- Eğitim materyalleri
- SSS
- İletişim kanalları
