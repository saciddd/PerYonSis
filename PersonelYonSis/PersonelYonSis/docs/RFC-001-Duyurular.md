RFC-001 – Duyurular Modülü
1. Amaç

PersonelYonSis uygulamasında sistem içi bilgilendirmeler, güncellemeler ve uygulama bazlı duyuruların kullanıcıya gösterilebilmesi için bir "Duyurular" modülü oluşturulur.
Duyurular, ana dashboard sayfasında tablo formatında görüntülenir; kullanıcılar uygulamaya göre filtreleme yapabilir ve yetkisi olan kişiler yeni duyuru ekleyebilir.
duyurular.html template oluşturulup index.html sayfasına include edilecektir. Sayfa 2 sütuna bölünecek sağ tarafında duyurular.html yer alacaktır.

2. Model Yapısı
Model: Duyuru

Yeni model PersonelYonSis uygulamasına eklenecek.

class Duyuru(models.Model):
    uygulama = models.CharField(max_length=100, help_text="Örn: mercis657, ik_core, genel")
    duyuru_metni = models.TextField()
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-olusturma_tarihi']  # yeniden eskiye

3. Yetki Kontrolü
Yetki Adı

"Genel Duyuru Ekleyebilir"

Bu yetkisi olmayan kullanıcı:

“Duyuru Ekle” butonunu göremez.

API üzerinden duyuru eklemeye kalkarsa:

{"status": "error", "message": "Bu işlem için yetkiniz yok."}

4. Endpointler & Fonksiyonlar
4.1. Duyuruları Listeleme

URL: /duyurular/
Metod: GET
Amaç:

HTML sayfasını render eder

Filtreleme için uygulama parametresi kullanılır (opsiyonel)

@login_required
def duyurular_list(request):
    uygulama = request.GET.get("uygulama")
    duyurular = Duyuru.objects.all()

    if uygulama:
        duyurular = duyurular.filter(uygulama=uygulama)

    uygulama_listesi = (
        Duyuru.objects.values_list("uygulama", flat=True).distinct()
    )

    return render(request, "common/duyurular.html", {
        "duyurular": duyurular,
        "uygulama_listesi": uygulama_listesi,
        "aktif_uygulama": uygulama,
    })

4.2. Duyuru Ekleme (AJAX – JSON Response)

URL: /duyurular/ekle/
Metod: POST

@login_required
def duyuru_ekle(request):
    if not request.user.has_permission("Genel Duyuru Ekleyebilir"):
        return JsonResponse({"status": "error", "message": "Bu işlem için yetkiniz yok."}, status=403)

    uygulama = request.POST.get("uygulama")
    metin = request.POST.get("duyuru_metni")

    if not uygulama or not metin:
        return JsonResponse({"status": "error", "message": "Tüm alanlar zorunludur."})

    duyuru = Duyuru.objects.create(
        uygulama=uygulama,
        duyuru_metni=metin,
        olusturan=request.user
    )

    return JsonResponse({"status": "success", "message": "Duyuru eklendi."})

5. HTML Tasarımı
5.1. Duyurular Tablosu

duyurular.html

<div class="card">
  <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0"><i class="bi bi-megaphone"></i> Duyurular</h5>

      <div class="d-flex gap-2">

          <!-- Uygulama Filtre -->
          <select id="appFilter" class="form-select form-select-sm" style="width:160px;">
            <option value="">Tümü</option>
            {% for app in uygulama_listesi %}
                <option value="{{ app }}" {% if aktif_uygulama == app %}selected{% endif %}>{{ app }}</option>
            {% endfor %}
          </select>

          <!-- Duyuru Ekle -->
          {% if request.user.has_permission("Genel Duyuru Ekleyebilir") %}
          <button class="btn btn-primary btn-sm" data-bs-toggle="modal" data-bs-target="#duyuruModal">
            <i class="bi bi-plus-circle"></i> Duyuru Ekle
          </button>
          {% endif %}
      </div>
  </div>

  <div class="card-body p-0">
     <table class="table table-striped mb-0">
        <thead class="table-light">
          <tr>
            <th>Uygulama</th>
            <th>Duyuru</th>
            <th>Oluşturan</th>
            <th>Tarih</th>
          </tr>
        </thead>

        <tbody>
        {% for d in duyurular %}
          <tr>
            <td>{{ d.uygulama }}</td>
            <td>{{ d.duyuru_metni }}</td>
            <td>{{ d.olusturan }}</td>
            <td>{{ d.olusturma_tarihi|date:"d.m.Y H:i" }}</td>
          </tr>
        {% endfor %}
        </tbody>
     </table>
  </div>
</div>

5.2. Duyuru Ekleme Modali
<div class="modal fade" id="duyuruModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header bg-light">
        <h5 class="modal-title"><i class="bi bi-plus-circle"></i> Yeni Duyuru</h5>
        <button class="btn-close" data-bs-dismiss="modal"></button>
      </div>

      <div class="modal-body">
        <form id="duyuruForm">
          {% csrf_token %}

          <label class="form-label">Uygulama</label>
          <input name="uygulama" class="form-control" placeholder="Örn: mercis657" required>

          <label class="form-label mt-2">Duyuru Metni</label>
          <textarea name="duyuru_metni" class="form-control" rows="4" required></textarea>
        </form>
      </div>

      <div class="modal-footer">
        <button class="btn btn-success" id="duyuruKaydetBtn">
            <i class="bi bi-check"></i> Kaydet
        </button>
      </div>
    </div>
  </div>
</div>

6. JavaScript – Kaydetme İşlemi
<script>
document.getElementById("duyuruKaydetBtn").addEventListener("click", function () {
    let form = document.getElementById("duyuruForm");
    let formData = new FormData(form);

    fetch("/duyurular/ekle/", {
        method: "POST",
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === "success") {
            Swal.fire("Başarılı", data.message, "success").then(() => {
                location.reload();
            });
        } else {
            Swal.fire("Hata", data.message, "error");
        }
    });
});
</script>

7. Filtreleme
document.getElementById("appFilter").addEventListener("change", function() {
    let value = this.value;
    let url = value ? "?uygulama=" + value : "";
    window.location = url;
});

Genel hatlar bu şekilde, yapı index.html dosyasına include edilip çalışacak biçimde kurgulanmalı. Gerekirse "appFilter" frontend'de çalışmalı tablo içi filtreleme yapıp tekrar istek atmamalı.
Duyurular tablosu max 10 satır ve paginated olmalı.