# Mercis Local - Request for Comments (RFC)

## 1. Giriş

Bu belge, Mercis Local uygulamasının geliştirilmesi için önerilen değişiklikleri ve iyileştirmeleri tartışmak amacıyla hazırlanmıştır. Bu RFC, uygulamanın mevcut durumunu, önerilen değişiklikleri ve bu değişikliklerin etkilerini ele alır.

## 2. Mevcut Durum

Mercis Local, FileMaker veritabanı ile entegre çalışan bir personel çizelge yönetim uygulamasıdır. Uygulama, birimlerin personel mesai planlamasını ve takibini kolaylaştırmayı hedeflemektedir. Mevcut uygulama, Tkinter tabanlı bir masaüstü uygulaması olarak geliştirilmiştir.

## 3. Önerilen Değişiklikler

### 3.1 Django'ya Geçiş

Mevcut uygulamanın Django tabanlı bir web uygulamasına dönüştürülmesi önerilmektedir. Bu değişiklik, uygulamanın daha geniş bir kullanıcı kitlesine ulaşmasını ve daha kolay yönetilmesini sağlayacaktır.

#### 3.1.1 Giriş ve Kimlik Doğrulama
- Kullanıcıların TC kimlik numarası ve şifre ile giriş yapabilmesi
- Kullanıcı adı ve şifre doğrulama işlemlerinin Django auth sistemi ile yapılması

#### 3.1.2 Çizelge Yönetimi
- Birim bazlı personel listeleme
- Tarih aralığı seçimi ve çizelge oluşturma
- Mesai ve izin bilgisi güncelleme
- Değişiklik geçmişi takibi

#### 3.1.3 Raporlama
- Personel bazlı mesai özeti
- Birim bazlı mesai dağılımı
- Tarih aralığı bazlı raporlar
- İzin kullanım raporları

### 3.2 Güvenlik İyileştirmeleri
- HTTPS protokolü kullanımı
- Oturum şifreleme
- Veri şifreleme ve güvenli dosya işlemleri

### 3.3 Performans İyileştirmeleri
- Sayfa yüklenme süresinin optimize edilmesi
- API yanıt süresinin optimize edilmesi
- Eşzamanlı kullanıcı desteğinin artırılması

## 4. Etkiler

### 4.1 Kullanıcı Deneyimi
- Daha modern ve kullanıcı dostu bir arayüz
- Daha hızlı ve verimli bir kullanıcı deneyimi

### 4.2 Teknik Altyapı
- Django tabanlı bir web uygulamasına geçiş
- Daha güvenli ve ölçeklenebilir bir altyapı

### 4.3 Geliştirme Süreci
- Mevcut kod tabanının yeniden yapılandırılması
- Yeni özelliklerin eklenmesi ve mevcut özelliklerin iyileştirilmesi

## 5. Sonuç

Bu RFC, Mercis Local uygulamasının daha modern, güvenli ve kullanıcı dostu bir hale getirilmesi için önerilen değişiklikleri ve iyileştirmeleri ele almaktadır. Önerilen değişikliklerin uygulanması, uygulamanın daha geniş bir kullanıcı kitlesine ulaşmasını ve daha kolay yönetilmesini sağlayacaktır.
