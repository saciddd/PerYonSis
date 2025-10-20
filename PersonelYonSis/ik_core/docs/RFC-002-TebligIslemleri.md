ik_core uygulamasına sistemde kayıtlı olan/olmayan personellere resmi yazı tebliğ etmek için bir Tebliğ Sistemi geliştirilecek.
ik_core uygulamasına eklenecek modeller:
class TebligImzasi:
ad = models.CharField(max_length=50)
metin = çok satırlı text(Örnek:
Doç. Dr. Sacit POLAT
Başhekim Yardımcısı)

class TebligMetni:
ad = models.CharField(max_length=100)
metin = uzun text(Örnek:
	Kayseri İl Sağlık Müdürlüğünün 01.01.2025 tarihli ve 123456 sayılı kararı ile Kayseri Devlet Hastanesine atama onay yazımı  okudum, 15.01.2025 tarihinde Hastanedeki görevime  başladığımı tebellüğ ettim.)

Eklenecek arayüzler, templateler ve tasarımları:
1 - TebligImzasi modelinin yönetildiği imza_tanimlari sayfası eklenecek.
- Sayfada tanımlanan tüm imzalar tablo biçiminde yer alacak.
- Tablonun 1. sütunu Kısa Ad(ad), 2. sütunu Metin(metin) olacak. metin alanı 3 satır yüksekliğinde yazı ortalanmış durumda. 3. sütunu işlemler sütunu işlem butonu icon biçiminde.
- Tablonun üstünde sağda İmza Ekle butonu yer alacak.
- Buton imza ekleme modalını açacak.
- imza ekleme/düzenleme modalı partials klasöründe yazılıp imza_tanimlari sayfasına include edilecek.
- imza düzenleme modunda açıldığında modalde sil butonu da yer alacak, sweet alert onayından sonra imza kaydını silecek.
- imza_tanimlari sayfası, teblig_imzasi_ekle, teblig_imzasi_sil endpointleri oluşturulacak.

2 - TebligMetni modelinin yönetildiği teblig_tanimlari sayfası eklenecek.
- Sayfada tanımlanan tüm Tebliğ Metinleri tablo biçiminde yer alacak.
- Tablonun 1. sütunu Kısa Ad(ad), 2. sütunu Metin(metin) olacak. metin alanı 3 satır yüksekliğinde yazı ortalanmış durumda. 3. sütunu işlemler sütunu işlem butonu icon biçiminde.
- Tablonun üstünde sağda Tebliğ Ekle butonu yer alacak.
- Buton Tebliğ ekleme modalını açacak.
- Tebliğ ekleme/düzenleme modalı partials klasöründe yazılıp teblig_tanimlari sayfasına include edilecek.
- Tebliğ düzenleme modunda açıldığında modalde sil butonu da yer alacak, sweet alert onayından sonra Tebliğ metni kaydını silecek.
- teblig_tanimlari sayfası, teblig_metni_ekle, teblig_metni_sil endpointleri oluşturulacak.

3 - Tebliğ İşlemlerinin yürütüldüğü teblig_islemleri sayfası eklenecek.
- Sayfa col-md-4 ve col-md-8 olarak iki sütuna bölünecek.
- Sol tarafta sırasıyla sağ yaslanmış vaziyette "kaydet ve yazdır" butonu,
- Aşağı açılır menü şeklinde tebliğ eden dropdown listesi. Bu seçimin hemen sağında düzenleme ikonu olacak ve imza tanımları sayfasına yönlendirecek.
- Altında aşağı açılır menü şeklinde tebliğ edilecek yazı dropdown listesi. Bu seçimin hemen sağında düzenleme ikonu olacak ve tebliğ tanımları sayfasına yönlendirecek.
- Altında seçili olan personelin bilgileri yer alacak. Şu şekilde:
Personel Adı Soyadı: {Personel.ad} {Personel.soyad}
Sicil No: {Personel.sicil_no}
Unvan: {Personel.unvan}
Branş: {Personel.brans}
Atama Karar Tarihi: {Personel.atama_karar_tarih}
Atama Karar No: {Personel.atama_karar_no}
DHY: {Personel.dhy}
DSS: {Personel.dss}
- Onun da altında sistemde kayıtlı olmayan personel checkboxu.
- Altında 3 satırlık personel bilgileri input alanı. 
----------
- Sayfanın sağ taraftaki sütunun da tebliğ tebellüğ belgesinin bir nevi ön izlemesi yer alacak.
- 1.satırda kalın harflerle "TEBLİĞ TEBELLÜĞ BELGESİ" ifadesi
- Altında 2 satır boşluk ve devamında iki yana yaslanmış vaziyette seçili tebliğ metni(Düzenlenebilir olacak)
- Metinden sonra bir satır boşluk ve 3 sütun;
-- Birinci sütunda "TEBLİĞ EDEN", 2. sütunda "TEBLİĞ TARİHİ", 3. sütunda "TEBELLÜĞ EDEN" ifadeleri ortalanmış biçimde yer alacak.
- Bunların altına yine 3 sütün;
-- 1. sütunda seçilmiş olan tebliğ imzasının metin alan
-- 2. sütunda "...../...../20...." İfadesi 
-- 3. sütunda eğer sistemde kayıtlı olmayan personel checkboxu işaretlenmişse; oradaki personel bilgileri input alanına yazılmış olan değer, aksi halde seçili personelin ad soyad, unvan ve sicil_no bilgileri alt alta yazılacak.
- Bu sayfadaki tebliğ metni alanı düzenlenebilir olacak.
- Kaydet ve yazdır dediğimizde bu sayfada ön izlemesini gördüğümüz tebliğ evrakı(col-md-8 olan kısım) yazdırılacak.
- TebligMetni.metin alanında yapılan değişiklikler kaydedilecek.
- "ik_core/teblig-islemleri/1/" biçiminde Tebliğ işlemleri sayfası endpointi tanımlanacak.
- teblig_metni_guncelle endpointi tanımlanacak.

- Gerekli fonksiyonlar oluşturulacak.