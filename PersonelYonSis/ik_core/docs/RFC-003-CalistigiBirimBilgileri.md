ik_core uygulamasında personellerin çalıştığı birim bilgilerini takip edebileceğimiz ve birim değişikliğine dair resmi yazıları hazırlayabileceğimiz bir sistem kurgulamalıyız.

- ik_core uygulamasına Aşağıdaki modeller eklenecek.
UstBirim:
ad = textfield Max len=100 (Örnek: Sağlık Bakım Hizmetleri Müdürlüğü, Başhekimlik)
Bina:
ad = textfield Max len=50
Birim: 
bina = Bina (Zorunlu)
ust_birim = UstBirim (Zorunlu)
ad = textfield Max len=50
PersonelBirim:
personel = Personel
birim = Birim
gecis_tarihi = date
sorumlu = bool
not = text max len=100
CreationTimestamp = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Zamanı")
created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Oluşturan")
- User modeli için "from PersonelYonSis.models import User"

- Üst Birim, Bina ve Birim tanımlarının yönetildiği sayfa @unvan_branstanimlari.html sayfasındaki yapıyla aynı olacak.
- Sayfanın sol tarafında "Bina Ekle" butonu ve sistemde kayıtlı binaların tablosu olacak.
- Tabloda [Bina Adı, Birim Sayısı, Seç] alanları olacak.
- Sayfanın sağ tarafında seçili binaya ait birimlerin listelendiği tablo yer alacak. 
- Tablonun üstünde Üst Birim Filtreleme için dropdownlist(Yanında Üst Birim ekleme modalı için + iconu şeklinde buton) ve birim ekle butonu yer alacak.
- Bina ekle butonu bina tanımlama modalını açacak. 
- Birim ekle butonu birim ekleme modelini açacak. Birim ekleme modalında eklenecek bina otomatik olarak görünecek.
- modaller partials klasöründe ayrı yazılıp include edilecek.
- Üst Birim, Bina ve birim ekleme için gerekli endpoint'ler oluşturulacak.

- personel_detay.html sayfası ve def personel_detay(request, pk): fonksiyonunu yeni yapıya uygun biçimde güncelleyelim.
- personel_detay fonksiyonu personelin en son çalıştığı birim bilgisini contexte göndermeli
- personel_detay.html sayfasındaki <div class="info-label">Çalıştığı Bina</div> kısmındaki spana {birim.bina} verisi yazılacak
- personel_detay.html sayfasındaki <div class="info-label">Birim</div> kısmındaki spana {birim.ad} verisi yazılacak
- bu alanların yanına Yeni Birim Belirleme ve Birim Geçmişi iconları konacak.
- İconlar buton biçiminde olacak.
- Yeni Birim Belirleme ve Birim Geçmişi sayfaları modal biçiminde açılacak, partials klasöründe ayrı yazılıp include edilecek.
- Yeni Birim Belirleme ve Birim Geçmişi için gerekli endpointler oluşturulacak.
- Yeni Birim Belirleme modalında sırasıyla Üst Birim, Bina, Birim, alt alta dropdown biçiminde seçilecek. Üst Birim ve Bina seçimine göre fetch isteği atılıp Birim Listesi güncellenecek.
- Altında gecis_tarihi, sorumlu, not alanları ve Kaydet butonu yer almalı.
- Birim Geçmişi modalında Personelin çalıştığı birim kayıtları yeniden eskiye doğru sıralanmalı.

- modaller dışındaki sayfa tasarımlarında bu etiketler kullanılacak:
{% extends "base.html" %}
{% block content %}
{% endblock %}
- css ve js kodları için:
{% block extra_css %}
{% endblock %}
{% block extra_js %}
{% endblock %}