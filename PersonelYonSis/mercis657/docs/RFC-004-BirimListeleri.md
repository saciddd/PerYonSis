🧩 RFC-004-BirimListeleri.md

Başlık: Birim Listeleri Yönetim Arayüzü
Uygulama: mercis657
Tarih: 2025-11-03
Hazırlayan: Sacit Polat

🎯 Amaç

Bu geliştirme ile kullanıcılar, Birim Yönetimi sayfası üzerinden:
Birimlere ait Personel Listelerini (dönem bazlı) görüntüleyebilecek,
Bu listelerdeki Personelleri inceleyebilecek,
Gerektiğinde listeden personel çıkarabilecek,
Personel olmayan listeleri silebilecekler.

Tüm işlemler, modal tabanlı bir arayüzle ve Ajax (fetch) üzerinden dinamik olarak yapılacak.
Sayfa yenilenmeden güncelleme yapılması ve SweetAlert2 ile kullanıcıya görsel geri bildirim verilmesi amaçlanmaktadır.

🧱 Model Yapısı

Kullanılan mevcut modeller:

class Birim(models.Model):
    BirimID = models.AutoField(primary_key=True)
    BirimAdi = models.CharField(max_length=100)
    # ... diğer alanlar ...

class PersonelListesi(models.Model):
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE, related_name='personel_listeleri')
    yil = models.PositiveIntegerField()
    ay = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    aciklama = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('birim', 'yil', 'ay')

class PersonelListesiKayit(models.Model):
    liste = models.ForeignKey(PersonelListesi, on_delete=models.CASCADE, related_name='kayitlar')
    personel = models.ForeignKey('Personel', on_delete=models.CASCADE)
    radyasyon_calisani = models.BooleanField(default=False)
    sabit_mesai = models.ForeignKey('SabitMesai', null=True, blank=True, on_delete=models.SET_NULL)
    sira_no = models.PositiveIntegerField(null=True, blank=True)

🧩 Yeni Özellikler
1️⃣ Birim Yönetimi Tablosu Güncellemesi

birim_yonetimi.html sayfasında her bir satırda İşlem kısmına (birim) yeni bir buton eklenecek:

<button class="btn btn-outline-secondary btn-sm" 
        onclick="openBirimListeleriModal({{ birim.BirimID }})" 
        title="Listeler">
    <i class="bi bi-card-checklist"></i>
</button>

2️⃣ Modal Yapısı
Ana modal — #birimListeleriModal

Modal ayrı html dosyası olarak yazılıp partials klasörüne kaydedilecek. birim_yonetimi.html dosyasına include edilecek.

Modal iki sütundan oluşur:

Sol Panel	Sağ Panel
İlgili birime ait PersonelListesi kayıtları (dönem bazlı) listelenir.
Her satırda “Personeller” ve “Listeyi Sil” butonları bulunur.	Seçilen listeye ait personeller listelenir.
Her satırda “Listeden Çıkar” butonu bulunur.
HTML Şablon (örnek)
<div class="modal fade" id="birimListeleriModal" tabindex="-1">
  <div class="modal-dialog modal-xl">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Birim Listeleri</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body d-flex">
        <div class="col-5 pe-3 border-end">
          <h6>Listeler</h6>
          <ul id="birimListeleriList" class="list-group"></ul>
        </div>
        <div class="col-7 ps-3">
          <h6>Personeller</h6>
          <ul id="listePersonellerList" class="list-group"></ul>
        </div>
      </div>
    </div>
  </div>
</div>

3️⃣ JavaScript — Modal Açma ve Veri Çekme
function openBirimListeleriModal(birimId) {
    fetch(`/mercis657/birim/${birimId}/listeler/`)
        .then(response => response.json())
        .then(data => {
            const listContainer = document.getElementById('birimListeleriList');
            listContainer.innerHTML = '';
            data.listeler.forEach(liste => {
                const li = document.createElement('li');
                li.classList.add('list-group-item', 'd-flex', 'justify-content-between');
                li.innerHTML = `
                    <span>${liste.ay}/${liste.yil}</span>
                    <div>
                        <button class="btn btn-outline-primary btn-sm me-2" onclick="showListePersoneller(${liste.id})">
                            <i class="bi bi-people-fill"></i> Personeller
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="deleteListe(${liste.id})">
                            <i class="bi bi-trash"></i> Sil
                        </button>
                    </div>`;
                listContainer.appendChild(li);
            });
            new bootstrap.Modal(document.getElementById('birimListeleriModal')).show();
        })
        .catch(err => Swal.fire('Hata', 'Listeler yüklenemedi: ' + err, 'error'));
}

4️⃣ Liste Personellerini Gösterme
function showListePersoneller(listeId) {
    fetch(`/mercis657/liste/${listeId}/personeller/`)
        .then(response => response.json())
        .then(data => {
            const personelList = document.getElementById('listePersonellerList');
            personelList.innerHTML = '';
            data.personeller.forEach(p => {
                const li = document.createElement('li');
                li.classList.add('list-group-item', 'd-flex', 'justify-content-between');
                li.innerHTML = `
                    <span>${p.ad} ${p.soyad}</span>
                    <button id="btnPersonelCikar" class="btn btn-outline-danger btn-sm" 
                        onclick="removePersonelFromListe(${listeId}, ${p.id})">
                        <i class="bi bi-x-circle"></i> Çıkar
                    </button>`;
                personelList.appendChild(li);
            });
        })
        .catch(err => Swal.fire('Hata', 'Personeller yüklenemedi: ' + err, 'error'));
}

5️⃣ Personel Silme Fonksiyonu
function removePersonelFromListe(listeId, personelId) {
    Swal.fire({
        title: 'Personeli Listeden Çıkar',
        text: 'Bu personeli listeden çıkarmak istediğinize emin misiniz?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Evet, çıkar',
        cancelButtonText: 'Vazgeç'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/mercis657/liste/${listeId}/personel/${personelId}/sil/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie('csrftoken'),
                    "Content-Type": "application/json"
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === "success") {
                    Swal.fire('Başarılı!', data.message, 'success');
                    showListePersoneller(listeId);
                } else {
                    Swal.fire('Hata!', data.message, 'error');
                }
            })
            .catch(err => Swal.fire('Hata!', 'Bir hata oluştu: ' + err, 'error'));
        }
    });
}

6️⃣ Liste Silme Fonksiyonu
function deleteListe(listeId) {
    Swal.fire({
        title: 'Listeyi Sil',
        text: 'Bu listeyi silmek istediğinize emin misiniz? (İlişkili personel yoksa silinir)',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Evet, sil',
        cancelButtonText: 'Vazgeç'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/mercis657/liste/${listeId}/sil/`, {
                method: 'DELETE',
                headers: { "X-CSRFToken": getCookie('csrftoken') }
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === "success") {
                    Swal.fire('Başarılı!', data.message, 'success');
                    openBirimListeleriModal(data.birim_id);
                } else {
                    Swal.fire('Hata!', data.message, 'error');
                }
            });
        }
    });
}

⚙️ Backend (View Fonksiyonları)

birim_listeleri(request, birim_id) → İlgili birime ait listeleri JSON döner.
liste_personeller(request, liste_id) → İlgili listeye ait personelleri JSON döner.
personel_cikar(request, liste_id, personel_id) → Kayıt siler.
liste_sil(request, liste_id) → Personel yoksa listeyi siler.

🧠 Güvenlik ve Yetki Kontrolü

Tüm işlemler:

if not request.user.has_permission('ÇS 657 Personel Liste Yönetimi'):
    return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)

🗂️ Beklenen JSON Örnekleri
/birim/<id>/listeler/
{
  "listeler": [
    {"id": 5, "ay": 10, "yil": 2025},
    {"id": 6, "ay": 11, "yil": 2025}
  ]
}

/liste/<id>/personeller/
{
  "personeller": [
    {"id": 12, "ad": "Ali", "soyad": "KAYA"},
    {"id": 15, "ad": "Merve", "soyad": "YILMAZ"}
  ]
}

📅 Sonuç
Bu geliştirme ile:
Birim bazlı listeler hiyerarşik ve modal yapıda yönetilebilecek,
Sayfa yenilenmeden liste/personel işlemleri yapılabilecek,
SweetAlert2 ile kullanıcıya anlık ve modern bildirimler sunulacak.