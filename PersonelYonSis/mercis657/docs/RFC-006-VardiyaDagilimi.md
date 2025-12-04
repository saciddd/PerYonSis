# RFC-006 - Vardiya Dağılımı Ekranı (Mercis657)

**Amaç**
Mercis657 uygulamasına günlük vardiya dağılımı ekranı eklemek. Yöneticiler/üst birim sorumluları seçilen kriterlere göre (kurum, üst birim, idareci, bina, gün, vardiya) sorgu yapıp, ilgili mesai kayıtlarını görecek; görev mahallinde olup olmadığını işaretleyip kaydedebilecekler.

---

## 1. Özet

* Üst bölüm: filtre alanları (Kurum, ÜstBirim, Idareci, Bina, Tarih, Vardiya tipi: Gündüz/Akşam/Gece) + `Kontrol Formu` ve `Kaydet` butonları (sağa yapışık).
* Alt bölüm: sorgu sonucu mesai kayıtları tablo biçiminde gösterilecek.
* Sadece aktif mesai tanımı (Mesai.MesaiTanim != null) listelenecek. İzin kayıtları gösterilmeyecek.
* Her satırda 'Görev Mahalinde?' (Evet/Hayır) radio butonları olacak; kullanıcı işaretleyip sayfa altındaki Kaydet ile topluca MesaiKontrol kayıtları oluşturacak/güncelleyecek.
* Kayıtlar Bina ve Birim bazında gruplanacak (frontend tarafında grouped table rows).

---

## 2. Yeni model

```python
class MesaiKontrol(models.Model):
    mesai = models.ForeignKey('Mesai', on_delete=models.CASCADE, related_name='mesai_kontrolleri')
    kontrol = models.BooleanField(default=False)
    kontrol_tarihi = models.DateTimeField(auto_now_add=True)
    kontrol_yapan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Mesai Kontrol'
        verbose_name_plural = 'Mesai Kontrolleri'
        unique_together = ('mesai',)
```

* `unique_together` ile aynı mesai için çoklu kontrol kaydı engellenir; güncellenir.

---

## 3. İlgili (var olan) modeller ilişkisi - özet

* `Kurum`, `UstBirim`, `Idareci`, `Bina`, `Birim`, `PersonelListesi`, `PersonelListesiKayit`, `Mesai`, `Personel`, `Mesai_Tanimlari` modelleri mevcut (kullanılacak alanlar yukarıdaki tanıma uygun).

---

## 4. Yetkilendirme

* Sayfaya erişim ve kaydetme işlemi için yetki kontrolü uygulanmalı. Örnek permission: `ÇS 657 Vardiya Dağılımı Sayfası` ve `ÇS 657 Vardiya Dağılımı Kontrolü`.
* Kontrol yetkisi yoksa sorgu görselleştirilmeli ama kaydetme butonu gizlenmeli veya disabled.

---

## 5. Endpointleri ve views (özet)

* `GET /mercis657/vardiya-dagilim/` -> Filtre formu + boş sonuç (veya default tarih) (template: `mercis657/vardiya_dagilim.html`).
* `POST /mercis657/vardiya-dagilim/search/` -> AJAX endpoint; filtrelere göre Mesai sorgusu döner (JSON) (sadece aktif MesaiTanim). Response: grouped by Bina->Birim arrays.
* `POST /mercis657/vardiya-dagilim/kaydet/` -> AJAX endpoint; gönderilen kontrolleri kaydeder/ günceller.

**Örnek view fonksiyonları** (kısa):

```python
@login_required
def vardiya_dagilim(request):
    # render template with select lists (kurumlar, ust_birimler, idareciler, binalar)

@login_required
@require_POST
def vardiya_dagilim_search(request):
    # JSON input: {kurum_id, ust_birim_id, idareci_id, bina_id, tarih, vardiya}
    # Query Mesai.objects.filter(MesaiDate=tarih, MesaiTanim__GecerliMesai=True)
    # join Birim via PersonelListesiKayit -> PersonelListesi -> birim or Personel->current birim mapping
    # Exclude Mesai with Izin not null
    # Build grouped response and return JsonResponse

@login_required
@require_POST
def vardiya_dagilim_kaydet(request):
    # JSON input: [{mesai_id:1, kontrol:true}, ...]
    # For each: MesaiKontrol.objects.update_or_create(mesai=mesai, defaults={'kontrol':val, 'kontrol_yapan':request.user})
```

---

## 6. Frontend (template + JS) - öneri

* Template: `mercis657/vardiya_dagilim.html`

  * Filtre form (selectler + tarih + vardiya radyo)
  * Sağ üstte `Kontrol Formu` ve `Kaydet` butonları. `Kontrol Formu` açıldığında seçilen kayıtlarda toplu Evet/Hayır yapma seçenekleri sunar.
  * Sonuç alanı: responsive table; grup başlıkları: Bina -> Birim. Her satır: Unvan | Personel Ad Soyad | Mesai Saat | Görev Mahalinde? (radio E/H)
* JS akışı:

  1. Filtre gönder -> fetch `/vardiya-dagilim/search/` -> JSON döner -> render grouped table.
  2. Kullanıcı radio butonları ile kontrol değerlerini ayarlar (her mesai satırı data-mesai-id içerir).
  3. Kaydet butonuna basınca toplanan `{mesai_id: kontrol}` nesnesi `/vardiya-dagilim/kaydet/` endpointine post edilir. Başarılı ise toast göster ve table güncelle (yalnız kontrol alanlarını disable/readonly yap veya görsel işaretle).

UI notları:

* Kaydet butonu disabled iken spinner göster, double-submit engelle.
* Yetki yoksa kaydet butonu gizlensin.

---

## 7. Migration ve deployment

* Yeni `MesaiKontrol` modeli için migration oluşturulacak.
* Yeni view/url eklemeleri ve template dosyaları eklenecek.

---

## 8. Örnek URL pattern (django)

```python
path('vardiya-dagilim/', views.vardiya_dagilim, name='vardiya_dagilim'),
path('vardiya-dagilim/search/', views.vardiya_dagilim_search, name='vardiya_dagilim_search'),
path('vardiya-dagilim/kaydet/', views.vardiya_dagilim_kaydet, name='vardiya_dagilim_kaydet'),
```

---

## 9. Ekstra özellikler

* PDF/CSV/Excel export (filtrelenmiş sonuçlar tablosu için) eklensin.

---