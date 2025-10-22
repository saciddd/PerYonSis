RFC-001 — Favori Mesailer

Uygulama: mercis657
Tarih: 2025-10-22
Hazırlayan: Sacit Polat

1. Amaç

mercis657 uygulaması bir çalışma listesi düzenleme sistemidir.
Kullanıcılar çizelge (çalışma tablosu) sayfası üzerinden personellerin mesai planlarını oluşturur.
Mevcut durumda sistem, @main_views.py dosyasındaki def cizelge fonksiyonunda yer alan:

mesai_tanimlari = Mesai_Tanimlari.objects.all()

komutu ile tüm mesai tanımlarını çekmekte ve cizelge.html sayfasına şu şekilde göndermektedir:

context["mesai_options"] = mesai_tanimlari

Bu veri, çizelge sayfasında dropdown listesi olarak kullanıcıya sunulur.
Ancak sistemde çok sayıda mesai tanımı bulunduğundan liste kalabalıklaşmakta ve kullanıcı deneyimi düşmektedir.

Bu RFC, kullanıcı bazlı Favori Mesailer sistemini tanımlamakta, kullanıcıların yalnızca sık kullandıkları mesai tanımlarına hızlı erişim sağlamasını amaçlamaktadır.

2. Teknik Tasarım
2.1 Model Yapısı

Favori mesailerin kullanıcı bazlı yönetimi için yeni bir model oluşturulacaktır:

class UserMesaiFavori(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favori_mesaileri")
    mesai = models.ForeignKey(Mesai_Tanimlari, on_delete=models.CASCADE, related_name="favori_kullanicilar")

    class Meta:
        unique_together = ('user', 'mesai')
        verbose_name = "Favori Mesai"
        verbose_name_plural = "Favori Mesailer"

    def __str__(self):
        return f"{self.user} → {self.mesai.Saat}"

2.2 Backend Fonksiyonları
get_favori_mesailer(user)

Yeni yardımcı fonksiyon main_views.py veya utils.py dosyasında tanımlanacaktır.

def get_favori_mesailer(user):
    """Kullanıcının favori mesailerini döndürür. Favori yoksa tüm mesailer gelir."""
    from mercis657.models import Mesai_Tanimlari, UserMesaiFavori

    favoriler = UserMesaiFavori.objects.filter(user=user).select_related("mesai")
    if favoriler.exists():
        return [f.mesai for f in favoriler]
    return Mesai_Tanimlari.objects.all()

favori_mesai_kaydet(request)

AJAX (fetch) isteğini karşılayacak basit bir API endpoint yazılır:

@login_required
def favori_mesai_kaydet(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Geçersiz istek."}, status=400)

    mesai_ids = json.loads(request.body.decode("utf-8")).get("mesai_ids", [])
    UserMesaiFavori.objects.filter(user=request.user).delete()

    for mid in mesai_ids:
        UserMesaiFavori.objects.create(user=request.user, mesai_id=mid)

    return JsonResponse({"status": "success"})

2.3 Çizelge Fonksiyonu Güncellemesi
def cizelge(request):
    ...
    mesai_tanimlari = get_favori_mesailer(request.user)
    context["mesai_options"] = mesai_tanimlari
    ...

2.4 Frontend (Modal & UI)
Favori Mesai Düzenleme Butonu

Çizelge sayfasında (üst menüde "İşlemler" ifadesinin yanında):
<label class="form-label small fw-bold">İşlemler</label>
Modal açan buton eklenecek:
<button class="btn btn-outline-warning btn-sm" onclick="openFavoriMesaiModal()">
  <i class="bi bi-star"></i> Favori Mesailer
</button>

modal dosyası partials klasörünün içinde yazılıp include edilecek.

Modal Yapısı:
<div class="modal fade" id="favoriMesaiModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header bg-light">
        <h5 class="modal-title">
          <i class="bi bi-star me-2"></i> Favori Mesailerini Seç
        </h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>

      <div class="modal-body">
        <div class="row row-cols-3 g-2" id="favoriMesaiListesi">
          {% for m in all_mesai_tanimlari %}
            <div class="col">
              <div class="form-check">
                <input class="form-check-input favori-mesai" type="checkbox" id="mesai{{ m.id }}"
                  value="{{ m.id }}"
                  {% if m.id in favori_ids %}checked{% endif %}>
                <label class="form-check-label" for="mesai{{ m.id }}">{{ m.Saat }} ({{ m.Sure }} saat)</label>
              </div>
            </div>
          {% endfor %}
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-primary" id="favoriMesaiKaydetBtn">
          <i class="bi bi-save"></i> Kaydet
        </button>
      </div>
    </div>
  </div>
</div>

JavaScript (fetch kaydetme)
<script>
function openFavoriMesaiModal() {
  new bootstrap.Modal(document.getElementById("favoriMesaiModal")).show();
}

document.getElementById("favoriMesaiKaydetBtn").addEventListener("click", function() {
  const secimler = Array.from(document.querySelectorAll(".favori-mesai:checked")).map(el => el.value);

  fetch("{% url 'mercis657:favori_mesai_kaydet' %}", {
    method: "POST",
    headers: {"X-CSRFToken": "{{ csrf_token }}"},
    body: JSON.stringify({mesai_ids: secimler})
  })
  .then(r => r.json())
  .then(data => {
    if (data.status === "success") {
      Swal.fire("Kaydedildi", "Favori mesaileriniz güncellendi.", "success").then(() => location.reload());
    } else {
      Swal.fire("Hata", data.message || "Kaydedilemedi", "error");
    }
  });
});
</script>

2.5 Çizelgedeki Dropdown Güncellemesi
Kaydedilen favoriler yenilendikten sonra, <select id="mesaiSelection"> içeriği backend’den gelen mesai_options listesini temel alır.

<select id="mesaiSelection" class="form-select" style="width: 110px;">
  <option value="">Mesai</option>
  {% for mesai in mesai_options %}
    <option value="mesai_{{ mesai.id }}">{{ mesai.Saat }}</option>
  {% endfor %}
</select>

3. Beklenen Sonuç
Kullanıcılar yalnızca kendi seçtikleri mesai tanımlarını dropdown’da görecek.
Tüm mesai listesini görmek isteyen kullanıcılar modal üzerinden favorilerini güncelleyebilecek.
Sistem yükü azalacak, çizelge sayfası daha hızlı yüklenecek.
Kullanıcı deneyimi iyileşecek.
