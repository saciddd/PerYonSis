ik_core uygulamamda Geçici Görevleri toplu kontrol edebileceğim bir yapı kurgulamalıyız.
Modelim bu şekilde:
class GeciciGorev(models.Model):
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE, related_name='gecicigorev_set')
    # GECICI_GOREV_TIPI alanı önemli, silinmeyecek!
    GECICI_GOREV_TIPI = (
        ('Gidis', 'Gidiş'),
        ('Gelis', 'Geliş'),
    )
    gecici_gorev_tipi = models.CharField(max_length=10, choices=GECICI_GOREV_TIPI, default='Gidis')
    gecici_gorev_baslangic = models.DateField()
    gecici_gorev_bitis = models.DateField(null=True, blank=True)
    asil_kurumu = models.CharField(max_length=150)
    gorevlendirildigi_birim = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.personel.full_name} - {self.gorevlendirildigi_birim} ({self.gecici_gorev_baslangic} - {self.gecici_gorev_bitis or 'devam'})"

- Geçici görevlendirmeler sayfasına girdiğimizde üst bölümde arama alanı yer alacak.
- Tarih seçimi yapıp ara dediğimizde o günü kapsayan geçici görev kayıtları tablo biçiminde listelenecek. Geliş yeşil, Gidiş Gri badge olacak.
- Arama formunun hemen altında sağda geçici görev kaydı ekle butonu yer alacak. Bu buton geçici görev kaydı ekleme modalını açacak.
- Modal partial klasöründe ayrı bir html dosyası olacak ve include edilecek.
- Modalde yer alan tabloya excelden kopyalanan kayıtlar yapıştırılıp kolayca geçici görev kayıtları eklenebilecek.
- Modaldeki çalışma prensibi çok önemli, sana daha önce hizmet_sunum_app'de kullandığım yapıyı atıyorum:
<!-- Personel Ekleme Modal -->
<div class="modal fade" id="personelEkleModal" tabindex="-1">
    {% csrf_token %}
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Personel Ekleme</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <!-- Sol Taraf: Önceki Dönem Personelleri -->
                    <div class="col-md-6">
                        <h6>Önceki Dönem Personelleri</h6>
                        <div class="table-responsive">
                            <table class="table table-sm" id="oncekiDonemTable">
                                <thead>
                                    <tr>
                                        <th><input type="checkbox" id="selectAllOnceki"></th>
                                        <th>T.C.</th>
                                        <th>Adı</th>
                                        <th>Soyadı</th>
                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
                        </div>
                        <button class="btn btn-primary" id="btnPersonelAktar">
                            <i class="bi bi-arrow-right"></i> Seçilenleri Aktar
                        </button>
                    </div>

                    <!-- Sağ Taraf: Manuel/Excel Giriş -->
                    <div class="col-md-6">
                        <h6>Yeni Personel Girişi</h6>
                        <div class="alert alert-info">
                            Excel'den kopyaladığınız verileri direkt tabloya yapıştırabilir veya manuel giriş yapabilirsiniz.
                            <br>Enter veya aşağı ok tuşu ile yeni satır ekleyebilirsiniz.
                        </div>
                        <div class="table-responsive">
                            <table class="table table-sm" id="yeniPersonelTable" style="border:2px solid #80a3d4;">
                                <thead>
                                    <tr>
                                        <th>Sıra No</th>
                                        <th>T.C.</th>
                                        <th>Adı</th>
                                        <th>Soyadı</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td style="width: 45px; min-width: 45px; max-width: 45px;">1</td>
                                        <td contenteditable="true" style="border:1px solid #80a3d4;"></td>
                                        <td contenteditable="true" style="border:1px solid #80a3d4;"></td>
                                        <td contenteditable="true" style="border:1px solid #80a3d4;"></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <button class="btn btn-success" id="btnPersonelKaydet">
                            <i class="bi bi-save"></i> Personelleri Ekle
                        </button>
                        <button class="btn btn-outline-danger ms-2" id="btnTabloyuBosalt">
                            <i class="bi bi-x-circle"></i> Tabloyu Temizle
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
// Personelleri ekle butonu
    document.getElementById('btnPersonelKaydet').addEventListener('click', function() {
        const donem = document.getElementById('donemSecimi').value;
        const birimId = document.getElementById('birimSecimi').value;
        if (!donem || !birimId) {
            alert('Lütfen dönem ve birim seçiniz');
            return;
        }

        const personeller = [];
        document.querySelectorAll('#yeniPersonelTable tbody tr').forEach(row => {
            const cells = row.querySelectorAll('td[contenteditable="true"]');
            if (cells.length === 3) {
                const personel = {
                    tc_kimlik: cells[0].textContent.trim(),
                    adi: cells[1].textContent.trim(),
                    soyadi: cells[2].textContent.trim()
                };
                if (personel.tc_kimlik && personel.adi && personel.soyadi) {
                    personeller.push(personel);
                }
            }
        });

        if (personeller.length === 0) {
            alert('Eklenecek personel bulunamadı!');
            return;
        }
        
        // CSRF token'ını modal içinden al
        const modalElement = document.getElementById('personelEkleModal');
        const csrfTokenInput = modalElement.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfTokenInput) {
            alert('CSRF token bulunamadı. Sayfayı yenileyip tekrar deneyin.');
            console.error('CSRF token input not found inside #personelEkleModal');
            return;
        }
        const csrfToken = csrfTokenInput.value;

        fetch('/hizmet_sunum/personel/kaydet/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken 
            },
            body: JSON.stringify({
                donem: donem,
                birim_id: birimId,
                personeller: personeller
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                fetchBildirimlerForSelected(); // Tabloyu güncelle
                // Modalı kapat (opsiyonel)
                var personelModal = bootstrap.Modal.getInstance(modalElement);
                if(personelModal) personelModal.hide();
            } else {
                throw new Error(data.message || 'Bilinmeyen bir hata oluştu.');
            }
        })
        .catch(error => {
            console.error('Kayıt hatası:', error);
            alert('Kayıt sırasında bir hata oluştu: ' + error.message);
        });
    });
    // Tablo işlemleri için fonksiyonlar
    function initYeniPersonelTable() {
        const table = document.getElementById('yeniPersonelTable');
        const tbody = table.querySelector('tbody');

        function addRowListeners(row) {
            row.querySelectorAll('td[contenteditable="true"]').forEach(cell => {
                cell.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' || e.key === 'ArrowDown') {
                        e.preventDefault();
                        addNewRow();
                    }
                });
            });
        }

        function addNewRow() {
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>${tbody.children.length + 1}</td>
                <td contenteditable="true"></td>
                <td contenteditable="true"></td>
                <td contenteditable="true"></td>
            `;
            tbody.appendChild(newRow);
            addRowListeners(newRow);
            newRow.querySelector('td[contenteditable="true"]').focus();
        }

        table.addEventListener('paste', function(e) {
            e.preventDefault();
            
            let data = e.clipboardData.getData('text');
            let rows = data.split('\n').filter(row => row.trim());
            
            tbody.innerHTML = '';
            
            rows.forEach((row, index) => {
                const cols = row.split('\t');
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td contenteditable="true">${cols[0] || ''}</td>
                    <td contenteditable="true">${cols[1] || ''}</td>
                    <td contenteditable="true">${cols[2] || ''}</td>
                `;
                tbody.appendChild(tr);
                addRowListeners(tr);
            });
        });

        addRowListeners(tbody.querySelector('tr'));
    }

- Şimdi dönelim Geçici görev kaydı tablomuza. Tabloda şu başlıklar yer alacak.
S. NO	TC KİMLİK NO	SİCİL NO	ADI	SOYADI	UNVAN	BRANŞ	KADRO BİRİM ADI	AKTİF BİRİM ADI G. GÖREV BAŞLANGIÇ TARİHİ   G. GÖREV BİTİŞ TARİHİ

- Tablonun üst kısmında sağda aşağı açılır liste şeklinde kurum listesi(Kurum Seçiniz(Required)) ve Kayıtları ekle butonu yer alacak.
- Kurum Listesinde "KADRO BİRİM ADI" ve "AKTİF BİRİM ADI" alanındaki benzersiz veriler alfabetik şekilde yer alsın. Bunun için js fonksiyonu hazırlayıp dropdown menünün soluna reflesh iconlu buton koyabiliriz.
- Kayıtları ekle dediğimizde tablodaki her kayıt için "TC KİMLİK NO" alanını kullanarak sistemden personel sorgusu yapacak sistemde var olan her personel için geçici görev kaydı oluşturacak.
- Kurum seçiniz alanında seçmiş olduğumuz kurum ilgili kaydın "KADRO BİRİM ADI" ile aynıysa gecici_gorev_tipi = "Gidis" olacak.
- Kurum seçiniz alanında seçmiş olduğumuz kurum ilgili kaydın "AKTİF BİRİM ADI" ile aynıysa gecici_gorev_tipi = "Gelis" olacak.
- Kayıt işlemi tamamlandığında kullanıcıya "Geçici Görev kayıtları tamamlandı: ... adet personelin geçici geliş, ... adet personelin geçici gidiş kaydı oluşturuldu. ... adet kayıt atlandı, sistemde kayıtları yok veya hatalı satırlar." şeklinde sweetalert uyarısı gösterelim.