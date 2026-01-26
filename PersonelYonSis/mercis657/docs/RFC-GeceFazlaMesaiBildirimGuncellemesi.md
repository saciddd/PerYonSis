# RFC-GeceFazlaMesaiBildirimGuncellemesi

## Özet
Bu RFC, `Bildirim` modeline eklenen gece çalışma (gündüz/gece ayrımı) alanlarının (`GeceNormalFazlaMesai`, `GeceBayramFazlaMesai`, vb.) sisteme entegrasyonu ve `bildirimler.html` sayfasının minimalist bir tasarıma kavuşturulması için yapılacak değişiklikleri kapsar.

## 1. Veritabanı ve Model
`Bildirim` modeli halihazırda aşağıdaki alanları içerecek şekilde güncellenmiştir:
- `GeceNormalFazlaMesai`
- `GeceBayramFazlaMesai`
- `GeceRiskliNormalFazlaMesai`
- `GeceRiskliBayramFazlaMesai`

## 2. Backend Değişiklikleri (`bildirim_views.py`)

### A. `bildirim_olustur`
- `hesapla_fazla_mesai` fonksiyonundan dönen `normal_gece_fazla_mesai` ve `bayram_gece_fazla_mesai` değerleri alınacak.
- `Bildirim` nesnesi oluşturulurken/güncellenirken bu değerler ilgili model alanlarına (`GeceNormalFazlaMesai`, `GeceBayramFazlaMesai`) kaydedilecek.
- `Riskli` gece alanları varsayılan olarak `0` atanacak (Riskli yönetimi ayrı modülde).

### B. `bildirim_listele`
- JSON yanıtına yeni eklenen gece alanları dahil edilecek:
  - `gece_normal_mesai`
  - `gece_bayram_mesai`
  - `gece_riskli_normal`
  - `gece_riskli_bayram`
- Toplam hesaplamalarında bu alanlar da dikkate alınacak.

### C. `update_risky_bildirim`
- Riskli bildirim yönetimi için gelen istekte, gece mesailerinin de riskli/risksiz dönüşümü desteklenecek.
- `changes` listesi içindeki objeler artık gece alanlarını da destekleyecek.

## 3. Frontend Tasarım ve Değişiklikler

### A. `bildirimler.html` - Minimalist Tasarım

Mevcut tablo yapısı çok fazla sütun içeriyor (Normal, Bayram, Riskli N, Riskli B, İcap N, İcap B vb.). Gece alanlarının eklenmesi tabloyu okunmaz hale getirebilir.

**Öneri:**
Tablo sütunlarını sadeleştirip, detayları "Gruplanmış" şekilde göstermek.

**Tablo Yapısı:**
1. **Personel**: Ad Soyad
2. **Normal Çalışma**:
   - Tek bir hücrede Gündüz ve Gece ayrımı alt alta veya yan yana ikonlu gösterim.
   - Örn: `10.0 ☀️ / 5.0 🌙`
   - Veya Toplam gösterip, tooltip ile detay.
   - **Karar**: Hücre içinde iki satır:
     `<div class="text-dark">10.0</div><div class="text-muted small">5.0 🌙</div>`
3. **Bayram Çalışma**: Aynı yapı.
4. **Riskli Çalışma**: Tek bir sütun altına toplanabilir veya modal detayına alınabilir. Ancak tabloda görülmesi önemliyse: `Normal Riskli / Bayram Riskli` şeklinde birleşik sütun.
5. **İcap**: Toplam İcap (Normal + Bayram). Detay tooltip veya modalda.
6. **Günlük Detaylar (1-31)**: Mevcut yapı korunabilir (çok genişletiyorsa gizlenebilir/scroll).
   - *Minimalist yaklaşım için*: Günlük sütunlar varsayılan olarak gizli gelebilir veya "Detay Göster" butonu ile açılabilir. Ancak personeller genellikle bu takvimi görmek ister. Takvim sütunlarını daraltıp sadece dolu günleri highlight etmek bir seçenek.
   - **Karar**: Gün sütunlarını koru ama genişliklerini minimumda tut.

**Aksiyonlar:**
- `bildirimTable` yapısı yeniden düzenlenecek.
- Sütunlar: `Normal (Gün/Gece)`, `Bayram (Gün/Gece)`, `Riskli (Top)`, `İcap (Top)`.
- JS render fonksiyonları (`updateSingleBildirimRow`, `updateBildirimTable`) bu yeni yapıya göre güncellenecek.
- "Riskli" sütunu sadece riskli mesai varsa değer gösterecek.

### B. `riskli_bildirim_yonetim.html`
- Modal içerisindeki tablo güncellenecek.
- **Sütunlar**:
  - Personel
  - Normal (Gündüz / Gece) -> Salt okunur
  - Bayram (Gündüz / Gece) -> Salt okunur
  - Riskli Normal (Gündüz / Gece) -> Input alanları
  - Riskli Bayram (Gündüz / Gece) -> Input alanları
- Kullanıcı arayüzünde çok fazla input kirliliği olmaması için "Gece Mesaileri" varsa ilgili inputların aktif olması veya ayrı bir sekmede yönetilmesi sağlanabilir.
- **Öneri**: Satır içi düzenleme yerine, her personel için "Risk Yönetimi" butonu ve o personele özel mini-modal veya accordion açılması.
- Ya da Tabloyu iki satırlı yapmak:
  - Satır 1: Gündüz Değerleri (Normal -> Riskli Normal, Bayram -> Riskli Bayram)
  - Satır 2: Gece Değerleri (Gece Normal -> Riskli Gece Normal, vb.) (Sadece gece mesaisi varsa görünür).

## 4. Uygulama Planı
1. `bildirim_views.py` backend mantığını güncelle.
2. `bildirimler.html` tablosu ve JS fonksiyonlarını güncelle (Minimalist tasarım).
3. `riskli_bildirim_yonetim.html` modülünü güncelle.
4. Test et.
