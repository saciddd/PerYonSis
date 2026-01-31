Çalışanların mesai hesaplamasında bir takım geliştirmeler yapacağız:
- class PersonelListesiKayit(models.Model): modeline "statu" alanı ekleyeceğiz. "Gündüz Personeli" ve "Nöbetli Çalışan" seçenekleri olacak.
- Bu alan personelin fazla mesai hesaplamasında esas teşkil edecek. O nedenle sistem performansı önemli gerekirse bool field olarak oluştur. Gündüz personeli ise true aksi halde false olsun. Bunu açıklama olarak belirt, unutulmasın.
- Aylık çalışma listelerine eklenen personellerin statülerini belirlemek için bir modal oluştur.
- Modalde tablo biçiminde personel listesi ve her personelin yanında statü seçimi için buttonlar olacak.
- Butonlar normalde gri renkte olacak. Seçim yapıldığında seçili olan butonun rengi gündüz çalışan için yeşil, nöbetli çalışan için kırmızı olacak. Seçim kaldırıldığında buton tekrar gri renge dönecek.
- Modalde ayrıca tümünü gündüz personeli yap ve tümünü nöbetli çalışan yap butonları olacak.
- Modal çizelge ve bildirim sayfalarına include edilecek.
- Çizelge sayfasında Hata Kontrolü ve Fazla Mesai Hesapla butonlarına tıklandığında öncelikle bu modal açılacak. Çünkü kontroller ve hesaplamalar bu statüye göre yapılacak.
- Personellerin statüleri boş bırakılamayacak. Her personelin statüsü belirlenmek zorunda.

# Hesaplama geliştirmeleri
- utils.py dosyasındaki "hesapla_fazla_mesai" fonksiyonunda statü kontrolü yapılacak. Gündüz personeli ise mevcut hesaplama yöntemi kullanılacak. Nöbetli çalışan ise fazla mesai hesaplaması şu şekilde yapılacak:
- Personelin çalışmaları tarih sırasına göre çekilecek.
- Personelin aylık çalışması gereken süre hesaplandıktan sonra, çalışması gereken süreyi doldurduktan soraki tüm çalışmaları fazla mesai olarak değerlendirilecek.
- Bu çalışmaların hepsi için Gece, gündüz, bayram gece, bayram gündüz ayrımı yapılmayacak.
- Toplam fazla mesai süresi öncelikle Bayram Gece, sonra Bayram Gündüz, sonra Normal Gece, sonra Normal Gündüz olacak şekilde dağıtılacak.

# Örnek hesaplama
- 20:00-08:00 arası gece, 08:00-20:00 arası gündüz olarak kabul edilmektedir.
- Personel: Ahmet Yılmaz
- Statü: Nöbetli Çalışan
- Ocak ayı Olması Gereken (saat): 176,00
- Fiili Çalışma (saat): 264,00
- Fazla Mesai (saat): 88,00
- Personel ayın 22,5,7,9,13,15,18,20,,22,27,30 tarihlerinde 08:00-08:00(24 saat) çalışmış olsun. Personel 8. çalışması olan 20 Ocak'ta 176 saat çalışmasını tamamlamış olacak. mesainin ilk 8 saati normal çalışma, kalan 16 saati fazla mesai olarak değerlendirilecek.
- Fazla Mesai Dağılımı:
  - Bayram Gece: 0,00
  - Bayram Gündüz: 0,00
  - Normal Gece: 48,00
  - Normal Gündüz: 40,00
- İlgili taihlerde bayram olması durumunda ekstra kontroller de yapılacak. Bunun için çalışan kodlar utils.py dosyasındaki hesapla_fazla_mesai fonksiyonunda zaten mevcut.

# Hata Kontrolü geliştirmeleri
- cizelge_kontrol_views.py dosyasındaki "cizelge_kontrol" fonksiyonunda statü kontrolü yapılacak. Gündüz personeli ise mevcut hata kontrolü kullanılacak. Nöbetli çalışan ise sadece personelin 5 gün üst üste mesaisinin boş bırakılıp bırakılmadığı kontrol edilecek.

# Bildirim sayfası geliştirmeleri
- bildirimler.html sayfasındaki "Tüm Personele Bildirim" butonuna tıklandığında include ettiğimiz modal açılacak. Bu modalda personellerin statüleri son kez belirlenecek. Kullanıcı olası değişiklikleri yapıp kaydet butonuna tıkladığında modal kapanacak ve statüye göre bildirimler oluşturulacak.