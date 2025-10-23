RFC-002 — Çizelge Sayfası Kullanıcı Deneyimi ve Fazla Mesai Gösterimi

Uygulama: mercis657
Tarih: 2025-10-23
Hazırlayan: Sacit Polat

1. Amaç

Bu RFC, cizelge.html sayfasındaki kullanıcı deneyimini artırmak ve fazla mesai bilgilerini dinamik biçimde göstermek amacıyla yapılacak düzenlemeleri tanımlar.

Mevcut durumda:
Çizelge tablosu (cizelgeTable) büyük olduğu için sayfa kaydırma deneyimi zayıftır.
Fazla mesai bilgileri anlık olarak hesaplanmamakta, kullanıcılar sadece tabloyu düzenleyebilmektedir.
Personel hücrelerinde ek açıklama veya not bilgisi gösterilmemektedir.
Bu dokümanda, çizelge tablosu görünümü ve fazla mesai hesaplamasının kullanıcı etkileşimiyle tetiklenmesi detaylandırılmaktadır.

2. Teknik Tasarım
2.1.1 Sabit Üst Başlık (Sticky Header)

Çizelge tablosundaki başlık satırı (thead) sabitlenecektir.
Kullanıcı tabloyu aşağı doğru kaydırsa dahi gün başlıkları (1, 2, 3...) sabit kalacaktır.

HTML
<table id="cizelgeTable" class="table table-bordered table-sm align-middle text-center">
  <thead class="table-light sticky-header">
    <tr>
      <th>S/N</th>
      <th>Personel Adı Soyadı</th>
      <th>Unvanı</th>
      {% for day in days %}
      <th class="{% if day.is_weekend %}weekend{% elif day.is_resmi_tatil %}resmi-tatil{% endif %}">
        {{ day.day_num }}
      </th>
      {% endfor %}
    </tr>
  </thead>
  <tbody>
    ...
  </tbody>
</table>

CSS
.sticky-header th {
    position: sticky;
    top: 0;
    background-color: #f8f9fa;
    z-index: 10;
    border-bottom: 2px solid #dee2e6;
}

2.1.2 Sabit Personel Bilgileri (Sticky columns)

Aynı yukarıda olduğu gibi [S/N, Personel Adı Soyadı, Unvanı] sütunları sabitlenecek, tablo sağa sola kaydırıldığında bu alanlar sabit şekilde görüntülenecektir.

2.2 Kaydırma Çubuklarının Her Zaman Görünür Olması

Büyük tabloların altına inmeden sağa kaydırmayı kolaylaştırmak için tablo bir scroll-container içerisine alınır.

HTML
<div class="table-responsive" style="max-height: calc(100vh - 250px); overflow: auto; padding-bottom: 10px;">
  <table id="cizelgeTable" class="table table-bordered table-sm align-middle text-center">
      ...
  </table>
</div>

CSS
.table-responsive {
    scrollbar-gutter: stable both-edges;
}


Bu sayede hem dikey hem yatay kaydırma çubukları her zaman görünür olacak ve sayfa sonuna inmeden erişilebilecektir.

2.3 Personel Hücresine Mesai Notu Badge Ekleme

Her personelin adının bulunduğu hücreye (personel detay ikonunun yanına) mesai notu gösterecek küçük bir badge eklenecektir.

HTML
<td class="position-relative">
  {{ personel.PersonelName }} {{ personel.PersonelSurname }}
  <i class="bi bi-person-circle text-primary ms-1 person-profile-btn"
     style="cursor: pointer; font-size: 0.9em;"
     data-personel-id="{{ personel.PersonelID }}"
     data-liste-id="{{ liste.id|default:0 }}"
     data-year="{{ current_year }}"
     data-month="{{ current_month }}"
     title="Personel Profili" role="button"></i>

  <span class="fazla-mesai-badge" style="display:none">
      -
  </span>
</td>

CSS
.fazla-mesai-badge {
    position: absolute;
    top: 2px;
    right: 4px;
    font-size: 0.75em;
    font-weight: bold;
    background: rgba(180,180,180,0.35);
    color: #000000;
    padding: 1px 5px;
    border-radius: 6px;
    z-index: 1;
    pointer-events: none;
}

2.4 Fazla Mesai Gösterimi
2.4.1 Yeni Buton

Sayfanın üst kısmındaki “İlk Liste Bildirimi” butonunun yanına “Fazla Mesaileri Göster” butonu eklenecektir:

<button id="showFazlaMesaiBtn" class="btn btn-outline-success btn-sm ms-2">
  <i class="bi bi-clock-history"></i> Fazla Mesaileri Göster
</button>

2.4.2 Backend Fonksiyonu

Kullanıcı butona bastığında fetch isteğiyle tetiklenecek endpoint:

from ..utils import hesapla_fazla_mesai
@login_required
def fazla_mesai_hesapla(request):
    year = int(request.GET.get("year"))
    month = int(request.GET.get("month"))
    liste_id = int(request.GET.get("liste_id"))

    kayitlar = PersonelListesiKayit.objects.filter(liste_id=liste_id).select_related("personel")

    sonuc = []
    for kayit in kayitlar:
        hesaplama = hesapla_fazla_mesai(kayit, year, month)
        sonuc.append({
            "personel_id": kayit.personel.PersonelID,
            "fazla_mesai": hesaplama
        })

    return JsonResponse({"status": "success", "data": sonuc})

2.4.3 JavaScript (Frontend Güncellemesi)
<script>
document.getElementById("showFazlaMesaiBtn").addEventListener("click", function() {
  const [year, month] = donem.split('/');
  const donem = document.getElementById('selectDonem').value; // YYYY/MM
  const listeId = document.getElementById('selectBirim').value;

  fetch(`/fazla-mesai-hesapla?year=${year}&month=${month}&liste_id=${listeId}`)
    .then(response => response.json())
    .then(data => {
      if (data.status === "success") {
        data.data.forEach(item => {
          const badge = document.querySelector(`#personel-${item.personel_id} .fazla-mesai-badge`);
          if (badge) {
            const fm = item.fazla_mesai;
            badge.textContent = `${fm > 0 ? '+' : ''}${fm}`;
            badge.style.background = fm > 0 ? "rgba(0,128,0,0.3)" : "rgba(255,0,0,0.3)";
            badge.style.display = "inline-block";
          }
        });
        Swal.fire("Tamamlandı", "Fazla mesailer hesaplandı.", "success");
      }
    });
});
</script>

Not: Her personel hücresine id="personel-{{ personel.PersonelID }}" eklenmelidir.

2.5 Performans Notları
Fazla mesai hesaplaması yoğun CPU kullanabileceğinden otomatik değil, kullanıcı tetiklemeli olacak.
Sadece ilgili ay ve liste bazlı sorgu yapılır.
Hesaplama backend tarafında optimize edilmelidir (select_related, prefetch_related kullanılmalı).

3. Beklenen Sonuç

✅ Çizelge tablosu üst satırı sabit kalacak.
✅ Kullanıcı tabloyu hem dikey hem yatay rahat kaydırabilecek.
✅ Fazla mesai hesaplamaları kullanıcı isteğiyle tetiklenecek.
✅ Mesai notları badge olarak gösterilecek.
✅ Fazla mesai değeri + ise yeşil, - ise kırmızı renkle görünecek.
✅ Sistem yükü minimum seviyede kalacak.