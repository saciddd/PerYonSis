# RFC-010 – Riskli Çalışma Hesaplaması ve Yönetimi

## Amaç

Bu doküman, Mercis 657 uygulamasındaki bildirimlerde **riskli çalışma sürelerinin** manuel giriş olmaksızın, mesai kayıtları üzerinden **deterministik ve otomatik** şekilde hesaplanmasını; buna bağlı arayüz ve süreç değişikliklerini tanımlar. Riskli çalışma süreleri, fazla mesai hesaplama fonksiyonunun **mevcut genel yapısını bozmadan** hesaplanacaktır.

Hedef;

* Kullanıcıdan saat bazlı manuel riskli süre girişi almamak
* Fazla mesai hesaplama fonksiyonunun **mevcut genel yapısını bozmamak**
* Riskli / normal ayrımını mesai bazında sade bir iş kuralı ile çözmek
* Bildirim üretim sürecini sadeleştirmek

---

## Kapsam

Bu RFC aşağıdaki alanları kapsar:

* Veri modeli değişiklikleri
* Riskli çalışma iş kuralları
* Fazla mesai hesaplama entegrasyonu
* Bildirim süreci sadeleştirmesi
* Çizelge ekranı UI/UX güncellemeleri

---

## Tanımlar

### Riskli Çalışma Türleri

Riskli çalışma, **Mesai** kaydı bazında aşağıdaki iki durumdan biri olabilir:

| Tür    | Açıklama                                                                     |
| ------ | ---------------------------------------------------------------------------- |
| Tam    | O günkü mesainin tamamı riskli kabul edilir                                   |
| Nöbet  | **hafta içi 16:00 sonrası** ve **hafta sonu çalışmanın tamamı** riskli kabul edilir |

---

## Veri Modeli Değişikliği

### Mesai Modeli

```python
class Mesai(models.Model):
    ...
    RISKLI_TAM = 'full'
    RISKLI_NOBET = 'nobet'

    RISKLI_CHOICES = [
        (RISKLI_TAM, 'Tam Riskli'),
        (RISKLI_NOBET, 'Nöbet Riskli'),
    ]

    riskli_calisma = models.CharField(
        max_length=10,
        choices=RISKLI_CHOICES,
        default=None,
        null=True,
        blank=True
    )
```

> Not: Risk bilgisi **kullanıcı tarafından süre olarak değil**, sadece tür olarak girilir.

---

## İş Kuralları

### 1. Riskli Süre Hesaplama Kuralları

#### Tam Riskli

* Mesainin tamamı riskli kabul edilir
* Bayram / gece ayrımı **mevcut hesaplama fonksiyonları** üzerinden devam eder

#### Nöbet Riskli

* Sadece **hafta içi** için geçerlidir
* Saat **16:00'dan sonra** başlayan kısımlar risklidir
* 16:00 öncesi süreler risksizdir

#### null durumda

* Riskli süre hesaplanmaz

---

### 2. Bayram ve Normal Gün Ayrımı

* Bayram ve normal gün ayrımı **mevcut `get_context()` fonksiyonu** üzerinden yapılmaya devam eder
* Riskli hesaplama, bu ayrımdan **sonra** uygulanır

---

### 3. Fazla Mesai Dağıtım Önceliği

Fazla mesai ödeme önceliği aşağıdaki sırayla uygulanır:

1. Riskli Bayram Fazla Mesai
2. Riskli Normal Fazla Mesai
3. Normal Bayram Fazla Mesai
4. Normal Fazla Mesai

Bu önceliklendirme, bildirim üretim aşamasında dikkate alınır.

---

## Fazla Mesai Hesaplama Entegrasyonu

* `hesapla_fazla_mesai(...)` fonksiyonunun **genel akışı korunur**
* Timeline/milestone mantığı bozulmaz
* Segment analizi sırasında:

  * Mesai.riskli_calisma alanı okunur
  * Segmentin riskli olup olmadığı hesaplanır

### Segment Bazlı Risk Kararı

| Risk Türü | Segment Riskli mi?                      |
| --------- | --------------------------------------- |
| none      | Hayır                                   |
| full      | Evet                                    |
| nobet     | Hafta içi + segment başlangıcı >= 16:00 |

> Not: Segmentler zaten 13:00 / 20:00 gibi kritik saatlerden bölündüğü için ek bölme gerekmez.

---

## Bildirim Süreci Değişiklikleri

### Devre Dışı Bırakılacak Alanlar

* **Riskli Çalışma Bildirimleri Yönetimi** modalı kaldırılacaktır (templates/mercis657/riskli_bildirim_yonetim.html)
* Aşağıdaki bileşenler silinecektir:

  * İlgili view fonksiyonları (update_risky_bildirim, update_risky_bildirim_all)
  * URL tanımları (urls.py)
  * Template parçaları

> Riskli çalışma artık **bildirimden sonra değil**, mesai aşamasında belirlenir.

---

## Çizelge Sayfası UI Güncellemeleri

### Yeni Buton

* Çizelge sayfasında(templates/mercis657/cizelge.html) "Fazla Mesai Bildirim" butonunun soluna:

```
[ Riskli Çalışmaları Belirle ]
```

butonu eklenecektir.
Turuncu renkli outline buton olacak.

---

### Riskli Çalışma Yönetim Ekranı

Butona basıldığında açılan modal / sayfa:

#### Tablo Alanları

| Alan                  | Açıklama                          |
| --------------------- | --------------------------------- |
| Personel Adı          | Ad Soyad                          |
| Toplam Riskli Süre    | Ay içindeki toplam riskli çalışma |
| Aylık Çalışma Günleri | Çizelge tablosuna benzer, Mesai yapılan günler tıklanabilir, diğerleri gri ve kapalı          |

#### Gün Bazlı İşlem

* Çalışılan gün hücreleri tıklanabilir
* Her gün için seçim:

  * Yok
  * Tam(Kırmızı hücre rengi)
  * Nöbet(Turuncu hücre rengi)

#### Toplu İşlemler

* Sayfa genelinde:

  * Tüm çalışmaları riskli yap
  * Tüm çalışmaları normal yap

* Personel bazında:

  * Personelin tüm çalışmalarını riskli yap
  * Personelin tüm çalışmalarını normal yap

---

## UX / UI İlkeleri

* Minimalist tasarım
* Tek ekran – modal karmaşası yok
* Hızlı toplu işlem
* Saat / süre girişi yok
* Kullanıcıya sadece **iş kuralı seçtirilir**

---

## Performans ve Bakım

* Hesaplama ek tablo gerektirmez
* Mesai başına tek alan kullanılır
* Geriye dönük düzeltme kolaydır
* Audit açısından net (hangi gün ne tür riskli?)

---

## Sonuç

Bu yaklaşım;

* Manuel veri girişini ortadan kaldırır
* Fazla mesai motorunu bozmadan genişletir
* Kullanıcıyı karmaşık muhasebe kararlarından kurtarır
* Denetlenebilir ve sürdürülebilir bir yapı sunar

