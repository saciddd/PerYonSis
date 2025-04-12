# Mutemetlik Uygulaması Gereksinim Dokümanı

## 1. Giriş
Bu doküman, Kurum Mutemetlik birimi tarafından kullanılacak olan Mutemetlik Uygulaması'nın gereksinimlerini detaylandırmaktadır.

## 2. Amaç
Mutemetlik Uygulaması, kurumun mutemetlik işlemlerini dijital ortama taşıyarak, iş süreçlerinin daha verimli ve takip edilebilir hale getirilmesini amaçlamaktadır.

## 3. Kapsam
Uygulama aşağıdaki temel modülleri içerecektir:

### 3.1. Personel Takibi
- Personel başlama ve ayrılma hareketlerinin takibi
- Personel durum değişikliklerinin kaydı
- Personel hareket geçmişi görüntüleme

### 3.2. Sendika Takibi
- Sendika üyelik giriş-çıkış işlemleri
- Sendika aidat takibi
- Sendika üyelik durumu raporlama

### 3.3. İcra Takibi
- İcra dosyalarının takibi
- İcra ödemelerinin kaydı
- İcra durumu raporlama

### 3.4. Ödeme Takibi
- Maaş ödemeleri takibi
- Avans ödemeleri takibi
- İkramiye ödemeleri takibi
- Diğer ödemelerin takibi

## 4. Fonksiyonel Gereksinimler

### 4.1. Personel Takibi
- Personel başlama/ayrılma hareketlerinin kaydedilmesi
- Hareket geçmişinin görüntülenmesi
- Hareket detaylarının düzenlenmesi
- Hareket raporlarının oluşturulması

### 4.2. Sendika Takibi
- Sendika üyelik giriş/çıkış işlemlerinin kaydedilmesi
- Üyelik durumu raporlarının oluşturulması
- Aidat takibinin yapılması
- Üyelik geçmişinin görüntülenmesi

### 4.3. İcra Takibi
- İcra dosyalarının kaydedilmesi
- İcra ödemelerinin takibi
- İcra durumu güncellemeleri
- İcra raporlarının oluşturulması

### 4.4. Ödeme Takibi
- Ödeme kayıtlarının tutulması
- Ödeme geçmişinin görüntülenmesi
- Ödeme raporlarının oluşturulması
- Ödeme detaylarının düzenlenmesi

## 5. Teknik Gereksinimler

### 5.1. Sistem Gereksinimleri
- Django 5.1.1
- Python 3.11
- PostgreSQL veritabanı
- Bootstrap 5.3.2
- jQuery 3.7.1

### 5.2. Güvenlik Gereksinimleri
- Kullanıcı yetkilendirme sistemi
- İşlem loglarının tutulması
- Veri şifreleme
- Güvenli oturum yönetimi

### 5.3. Performans Gereksinimleri
- Sayfa yüklenme süresi < 2 saniye
- Eşzamanlı kullanıcı sayısı > 50
- Veritabanı sorgu optimizasyonu

## 6. Kullanıcı Arayüzü Gereksinimleri
- Modern ve kullanıcı dostu arayüz
- Responsive tasarım
- Kolay navigasyon
- Anlaşılır form yapıları
- Detaylı raporlama ekranları

## 7. Raporlama Gereksinimleri
- Excel export özelliği
- PDF rapor oluşturma
- Özelleştirilebilir rapor şablonları
- Filtreleme ve sıralama özellikleri

## 8. Entegrasyon Gereksinimleri
- PersonelYonSis uygulaması ile entegrasyon
- Merkezi veritabanı entegrasyonu
- E-imza entegrasyonu
- E-fatura entegrasyonu

## 9. Test Gereksinimleri
- Unit testler
- Integration testler
- Kullanıcı kabul testleri
- Performans testleri

## 10. Bakım ve Destek Gereksinimleri
- Düzenli yedekleme
- Hata takip sistemi
- Kullanıcı destek sistemi
- Dokümantasyon güncellemeleri 