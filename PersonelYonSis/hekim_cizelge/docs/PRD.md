Hekim Çizelge Uygulaması - PRD (Product Requirements Document)
1. Genel Bakış
Hekim Çizelge Uygulaması, hastane personelinin çalışma çizelgelerinin yönetimi, kontrolü ve raporlanması için geliştirilmiş bir sistemdir.
2. Hedefler
•	Hastane personelinin aylık çalışma çizelgelerinin etkin yönetimi
•	Çalışma saatlerinin ve görevlerin çakışmasının önlenmesi
•	Fazla mesai ve icap nöbetlerinin otomatik hesaplanması
•	Çizelgelerin onay süreçlerinin yönetimi
•	Raporlama ve analiz imkanı
3. Kullanıcı Rolleri
3.1 Çizelge Hazırlayıcı
•	Aylık çizelgeleri oluşturma
•	Personel görevlendirmelerini yapma
•	Değişiklik talepleri oluşturma
3.2 Kontrol Yetkilisi
•	Hazırlanan çizelgeleri kontrol etme
•	Onay/Red işlemleri yapma
•	Değişiklik talep etme
3.3 Yönetici
•	Tüm çizelgelere erişim
•	Raporları görüntüleme
•	Sistem parametrelerini yönetme
4. Temel Özellikler
4.1 Çizelge Yönetimi
•	Aylık bazda çizelge oluşturma
•	Personel görev ataması
•	Birim bazlı görüntüleme
•	Çakışma kontrolü
•	Varsayılan hizmet tanımlama
•	Toplu güncelleme imkanı
4.2 Kontrol Mekanizmaları
•	Aynı gün içinde çakışan görevlerin kontrolü
•	Yasal çalışma süreleri kontrolü
•	Zorunlu dinlenme süreleri kontrolü
•	Birim bazlı personel yetkinlik kontrolü
4.3 Onay Süreci
•	Hazırlanan çizelgelerin onaya sunulması
•	Çok aşamalı onay akışı
•	Değişiklik tarihçesi
•	Red durumunda gerekçe bildirimi
4.4 Mesai Hesaplamaları
•	Normal mesai süreleri
•	Fazla mesai süreleri
•	İcap nöbeti süreleri
•	Resmi tatil mesaileri
•	Hafta sonu çalışma süreleri
4.5 Raporlama
•	Personel bazlı çalışma raporları
•	Birim bazlı çalışma raporları
•	Gün bazlı çalışma raporları
•	Hafta bazlı çalışma raporları
•	Mesai özet raporları
•	İcap nöbeti raporları
•	Onay durumu raporları
5. Teknik Gereksinimler
5.1 Sistem Altyapısı
•	Django web framework
•	PostgreSQL veritabanı
•	Modern web tarayıcı desteği
•	Responsive tasarım
5.2 Güvenlik
•	Rol bazlı yetkilendirme
•	İşlem logları
•	Veri değişiklik tarihçesi
•	SSL/TLS güvenliği
6. Kullanıcı Arayüzü
6.1 Çizelge Görünümü
•	Ay bazlı takvim görünümü
•	Hekim bazlı görünüm
•	Hizmet bazlı görünüm
•	Kolay gezinme ve filtreleme
•	Drag-drop desteği
6.2 Veri Girişi
•	Toplu veri girişi
•	Hızlı düzenleme
•	Şablon kullanımı
•	Otomatik tamamlama
7. Entegrasyonlar
•	Hastane bilgi sistemi entegrasyonu
•	Personel bilgi sistemi entegrasyonu
•	E-posta bildirim sistemi
•	Mobil uygulama desteği
8. Performans Gereksinimleri
•	Sayfa yüklenme süresi < 3 saniye
•	Eşzamanlı 100+ kullanıcı desteği
•	5+ yıllık veri saklama
•	Günlük yedekleme
9. İleriki Geliştirmeler
•	Mobil uygulama
•	Otomatik çizelge önerisi
•	Yapay zeka destekli optimizasyon
•	Gerçek zamanlı bildirimler
