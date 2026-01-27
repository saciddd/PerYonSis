# RFC: Etkileşimli Kampus Görev Noktası Analiz Sistemi
1. Amaç ve Kapsam
Kullanıcıların statik bir liste yerine, kampüs krokisi/renderı üzerinde binaları görsel olarak seçebildiği, bina bazlı personel ve birim metriklerini (kat sayısı, personel sayısı, birim dağılımı) anlık olarak görebildiği bir modülün hayata geçirilmesi.

2. Model Güncellemeleri (Database Schema)
Mevcut modellere Kampus kavramını eklememiz ve binaları bu kampüslere bağlayıp koordinatlandırmamız gerekiyor.

Python

# ik_core/models.py (veya ilgili dosya)

class Kampus(models.Model):
    ad = models.CharField(max_length=100, verbose_name="Kampüs Adı")
    gorsel = models.ImageField(upload_to='kampus_krokileri/', verbose_name="Kampüs Krokisi/Render")
    
    class Meta:
        verbose_name = "Kampüs"
        verbose_name_plural = "Kampüsler"

    def __str__(self):
        return self.ad

# Bina Modelini Güncelleme
# Not: Mevcut Bina modelinize aşağıdaki alanları ekleyin
class Bina(models.Model):
    # ... mevcut alanlar (ad) ...
    kampus = models.ForeignKey(Kampus, on_delete=models.SET_NULL, null=True, related_name='binalar')
    aciklama = models.CharField(max_length=100, blank=True, null=True, verbose_name="Açıklama: Örneğin Kat Bilgisi (Örn: 3 Katlı)")
    # Harita üzerinde işaretleme için SVG koordinatlarını tutacak alan
    koordinatlar = models.TextField(blank=True, null=True, help_text="SVG Polygon noktaları (x1,y1 x2,y2...)")

    # Meta ve __str__ aynı kalabilir
3. Backend Mantığı (View Geliştirme)
Mevcut birim_analiz_view fonksiyonunuzun mantığını koruyarak, bina bazlı veri setini güçlendirecek bir yapı kurmalıyız.

İş Akışı:

Filtreleme Personel seçimi ve Kampüs seçimi şeklinde olmalı (Personel filtrelemesi için analiz_views.py dosyasındaki def birim_analiz_view(request): fonksiyonu kopyalanabilir, çalışma mantığı aynı olmalı).

Ardından bulunan veri seti üzerinden;
Kampüs seçimi ile ilgili kampüsteki binaların listelenmesi.

Her bina için:

Bağlı birimlerin sayılması.

Bu birimlerde çalışan (filtreye uyan) personellerin sayılması.

Modal için birim bazlı personel listesinin hazırlanması.
gerekmekte.

4. Front-End: Etkileşimli Harita (JS & CSS)
Görsel üzerindeki alanları işaretlemek için en stabil yöntem SVG Overlay kullanmaktır.

HTML Yapısı
HTML

<div class="kampus-container" style="position: relative; display: inline-block;">
    <img src="{{ kampus.gorsel.url }}" id="kampus-image" style="width: 100%; height: auto;">
    <svg id="kampus-svg" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
        {% for bina in bina_verileri %}
        <polygon points="{{ bina.koordinatlar }}" 
                 class="bina-area" 
                 data-bina-id="{{ bina.id }}"
                 data-ad="{{ bina.ad }}"
                 data-kat="{{ bina.kat_bilgisi }}"
                 data-birim="{{ bina.birim_sayisi }}"
                 data-personel="{{ bina.personel_sayisi }}"
                 style="fill:rgba(0, 123, 255, 0.3); stroke:#007bff; stroke-width:2; cursor:pointer;">
        </polygon>
        {% endfor %}
    </svg>
</div>
JS Etkileşimi (Hover ve Click)
AdminLTE içinde bulunan Bootstrap popover/tooltip özelliklerini kullanarak bina bilgilerini gösterebiliriz:

JavaScript

$('.bina-area').hover(function(e) {
    let data = $(this).data();
    let content = `
        <b>${data.ad}</b><br>
        Kat: ${data.kat}<br>
        Birim: ${data.birim}<br>
        Personel: ${data.personel}
    `;
    // Tippy.js veya Bootstrap Tooltip tetikleme
    showTooltip(e, content);
}, function() {
    hideTooltip();
});

$('.bina-area').click(function() {
    let binaId = $(this).data('bina-id');
    // AJAX ile Bina detaylarını (birim bazlı personel) getir ve Modalı aç
    loadBinaDetailModal(binaId);
});
5. Implementasyon Adımları (Antigravity İçin Talimatlar)
Aşağıdaki sırayı takip etmesini isteyebilirsiniz:

Migrate: Kampus modelini oluştur ve Bina modeline kampus, aciklama, koordinatlar alanlarını ekle.

Admin Update: Kampüs tanımları sayfası oluştur, kampüs görseli üzerinden JS "Coordinate Picker" ile bina kordinatlarını elde et ve Bina modeline kaydet.

Analysis Logic: birim_analiz_view fonksiyonunu, seçilen kampüsteki binaları dönecek ve her bina için annotate veya Python seviyesinde gruplandırma yaparak personel sayılarını hesaplayacak şekilde güncelle.

Template: AdminLTE uyumlu yeni bir analiz sayfası oluştur. Sorgu / filtre sayfası ayrı, Kampüs görselinin (SVG overlay ile) yer aldığı analiz sayfası ayrı.

Modal: Bina tıklandığında açılacak, içinde DataTables barındıran ve birim/personel detaylarını gösteren modülü ayrıo dosya olarak hazırla. include edilecek.

6. Teknik Notlar
Koordinatlar: Görselin üzerine çizilecek poligonlar için 0,0 100,0 100,100 0,100 gibi (yüzdelik tabanlı) veya sabit pixel bazlı koordinatlar kullanılabilir. Responsive olması için yüzdelik (viewBox) kullanımı önerilir.

Performans: Personel filtreleme işlemini, mevcut fonksiyonunuzdaki gibi prefetch_related ile optimize etmeye devam edin; bina bazlı sayımları Counter nesneleriyle bellek içinde yapın.