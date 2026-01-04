# RFC-004 – Personel Analiz Sayfaları

## Amaç

Bu doküman, **ik_core** uygulaması içerisinde geliştirilecek olan **Personel Dashboard & Analiz Sayfaları** mimarisini tanımlar. Amaç; kurumdaki personel verilerini **ünvan** ve **birim** perspektiflerinden analiz edilebilir, filtrelenebilir, dışa aktarılabilir ve yönetsel kararları destekleyecek şekilde sunmaktır.

Bu RFC, **tamamen ik_core modelleriyle çalışan**, modern ve sürdürülebilir bir yapı oluşturmayı hedefler.

---

## Kapsam

Bu RFC aşağıdaki ekranları kapsar:

1. **Personel Dashboard (Giriş Sayfası)**
2. **Ünvan Bazlı Analiz Sayfası**
3. **Birim Bazlı Analiz Sayfası**

Kapsam dışı:

* Personel Kontrol Formu (ileride ayrı RFC)
* Performans / mesai / vardiya analizleri

---

## 1. Personel Dashboard (Giriş)

### Genel Yapı

Dashboard ilk açıldığında kullanıcıyı iki büyük kart karşılar:

* **Ünvan Bazlı Analiz**
* **Birim Bazlı Analiz**

Kartlar:

* Minimalist
* Büyük ikonlu
* Tıklanabilir
* Mobil uyumlu

Her kart ilgili analiz sayfasına yönlendirir.

---

## 2. Ünvan Bazlı Analiz Sayfası

### Sayfa Yapısı

Sayfa iki ana bölümden oluşur:

#### A. Üst Bölüm – Filtre & Görünüm Ayarları

Bu bölüm **sorguya dahil edilecek personelleri** ve **tablonun nasıl gösterileceğini** belirler.

##### Filtre Alanları

* Personel Durumu (Aktif / Pasif / Kurumdan Ayrıldı / Asıl Kurumuna Döndü)
* Kısa Unvan
* Kadro Durumu (Kadrolu / Geçici Gelen)

Kısa Unvan alanı personel_list.html sayfasındaki yapının aynısı olmalı:
<div class="col-md-2">
    <label for="kisa_unvan" class="form-label">Kısa Unvan</label>
    <button type="button" class="btn btn-outline-secondary w-100 d-flex justify-content-between align-items-center" data-bs-toggle="modal" data-bs-target="#kisaUnvanModal" style="font-size: 0.85rem; padding: 4px 8px; border-color: #ced4da; height: 35px;">
        <span id="kisaUnvanSelectBtnLabel" class="text-truncate">Seçiniz...</span>
        <span id="kisaUnvanSelectBtnBadge" class="badge bg-primary rounded-pill d-none ms-1">0</span>
        <i class="bi bi-chevron-down ms-1 small text-muted"></i>
    </button>
</div>
{% include 'ik_core/partials/kisa_unvan_modal.html' %}

> Filtreler birden fazla seçilebilir olmalıdır.

##### Görünüm Ayarları

* Gruplama türü (Kısa Ünvan)
* Tablo yoğunluğu (Normal / Sıkışık)
* Sayfa başına kayıt sayısı

---

#### B. Alt Bölüm – Analiz Sekmeleri & Tablolar

##### Sekmeler

* Kısa Ünvan Dağılımı
* Birim – Kısa Ünvan Kırılımı

##### Tablo Özellikleri

* Dinamik kolonlar
* Sıralama
* Arama
* Hücre tıklanabilirliği

Bir hücreye tıklandığında:

* İlgili personel listesi modal olarak açılır

Modal içerikleri:

* Ad Soyad
* Telefon
* Yaş
* Ünvan / Branş
* Kadro Durumu
* Özel Durumlar

##### Dışa Aktarım

* PDF
* Excel

(Modal içeriği veya tüm tablo için)

---

## 3. Birim Bazlı Analiz Sayfası

### Temel Fark

Bu sayfa, Ünvan Bazlı Analiz’e benzer yapıdadır ancak **odak noktası birimdir**.

### Üst Filtre Alanları

* Personel Durumu
* Birimin Bağlı Olduğu Üst Birim (**Birim.ust_birim**)
* Ünvanın Bağlı Olduğu Makam (**KisaUnvan.ust_birim**) – *ekstra filtre*
* Kadro Durumu

> Bu yapı sayesinde örneğin:
> **Başhekimlik makamına bağlı Kalite Birimi’nde çalışan hemşireler** listelenebilir.

---

### Alt Bölüm – Birim Dağılım Analizi

Sekmeler:

* Üst Birim → Birim Dağılımı
* Birim → Ünvan Dağılımı

Tablo özellikleri Ünvan Bazlı Analiz ile aynıdır.

---

## Kullanılacak Temel Modeller

Bu ekranlar **yalnızca ik_core modelleriyle** çalışacaktır.

Başlıca modeller:

* Personel
* Unvan
* Brans
* UnvanBransEslestirme
* KisaUnvan
* Birim
* UstBirim
* PersonelBirim

---

Tüm modaller templates/ik_core/partials klasörüne yazılıp include edilmeli.

---

## Teknik Notlar

* Frontend: Bootstrap + minimal JS (tercihen vanilla)
* Grafikler: Chart.js / ECharts (opsiyonel)
* Büyük veri için server-side pagination
* Filtreler querystring ile taşınmalı (bookmarklanabilir)

---

---

## Sonuç

Bu RFC ile hedeflenen yapı:

* Kurumsal karar destek mekanizmalarına uygun
* Uzun vadede genişletilebilir

bir **Personel Analiz Altyapısı** oluşturmaktır.
