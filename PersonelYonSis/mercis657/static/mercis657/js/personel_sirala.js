document.addEventListener('DOMContentLoaded', function () {
    const modal = document.getElementById('personelSiralaModal');
    const list = document.getElementById('sortable-list');
    let sortable = null;

    // CSRF token
    const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let saveUrl = window.saveUrl || '';

    // Modal açıldığında Sortable başlat
    modal.addEventListener('shown.bs.modal', function () {
        if (!sortable) {
            sortable = Sortable.create(list, { animation: 150 });
        }
    });

    // Alfabetik sıralama
    document.getElementById('sirala-alfabetik').addEventListener('click', function () {
        const items = Array.from(list.children);
        items.sort((a, b) => {
            const nameA = a.dataset.adsoyad || a.textContent.toLowerCase();
            const nameB = b.dataset.adsoyad || b.textContent.toLowerCase();
            return nameA.localeCompare(nameB, 'tr');
        });
        items.forEach(li => list.appendChild(li));
    });

    // Unvana göre sıralama
    document.getElementById('sirala-unvan').addEventListener('click', function () {
        const items = Array.from(list.children);
        items.sort((a, b) => {
            const unvanA = a.dataset.unvan || '';
            const unvanB = b.dataset.unvan || '';
            // Unvan eşitse adsoyad ile alfabetik sırala
            if (unvanA === unvanB) {
                const nameA = a.dataset.adsoyad || a.textContent.toLowerCase();
                const nameB = b.dataset.adsoyad || b.textContent.toLowerCase();
                return nameA.localeCompare(nameB, 'tr');
            }
            return unvanA.localeCompare(unvanB, 'tr');
        });
        items.forEach(li => list.appendChild(li));
    });

    // Sıralamayı Sıfırla (ilk sıralama: sira_no'ya göre)
    document.getElementById('siralama-reset').addEventListener('click', function () {
        const items = Array.from(list.children);
        items.sort((a, b) => {
            const snA = parseInt(a.textContent.split('-')[0]) || 0;
            const snB = parseInt(b.textContent.split('-')[0]) || 0;
            return snA - snB;
        });
        items.forEach(li => list.appendChild(li));
    });

    // Önceki Ay Sıralaması
    document.getElementById('sirala-onceki-ay').addEventListener('click', function () {
        const btn = this;
        const originalHtml = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Yükleniyor...';
        
        // Liste ID'yi al (saveUrl'den parse et)
        const listeId = saveUrl.match(/\/personel-listesi\/(\d+)\//)?.[1];
        if (!listeId) {
            alert('Liste ID bulunamadı.');
            btn.disabled = false;
            btn.innerHTML = originalHtml;
            return;
        }
        
        fetch(`/mercis657/personel-listesi/${listeId}/onceki-ay-siralamasi/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrftoken
            }
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.status === 'success') {
                const siralamasi = data.siralamasi;
                
                // Mevcut kayıtları al
                const items = Array.from(list.children);
                
                // Önceki ay sıralamasına göre sırala
                items.sort((a, b) => {
                    const personelIdA = parseInt(a.dataset.personelId) || 0;
                    const personelIdB = parseInt(b.dataset.personelId) || 0;
                    
                    const siraNoA = siralamasi[personelIdA];
                    const siraNoB = siralamasi[personelIdB];
                    
                    // Eğer önceki ay sıralamasında yoksa, en sona koy
                    if (siraNoA === undefined && siraNoB === undefined) {
                        return 0; // İkisi de yoksa, mevcut sırayı koru
                    }
                    if (siraNoA === undefined) return 1; // A yoksa, B'den sonra
                    if (siraNoB === undefined) return -1; // B yoksa, A'dan sonra
                    
                    return siraNoA - siraNoB;
                });
                
                // DOM'a uygula
                items.forEach(li => list.appendChild(li));
                
                btn.disabled = false;
                btn.innerHTML = originalHtml;
            } else {
                alert('Hata: ' + (data.message || 'Bilinmeyen hata'));
                btn.disabled = false;
                btn.innerHTML = originalHtml;
            }
        })
        .catch(err => {
            alert('Sunucu hatası: ' + err);
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        });
    });

    // Kaydet butonu
    document.getElementById('siralama-kaydet').addEventListener('click', function () {
        const payload = Array.from(list.children).map((li, idx) => ({
            id: li.dataset.kayitId,
            sira_no: idx + 1
        }));
        fetch(saveUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ order: payload })
        })
        .then(resp => resp.json())
        .then(data => {
            if (data.status === 'success') {
                // Toast/alert
                alert('Sıralama kaydedildi.');
                // Modal kapat
                const bsModal = bootstrap.Modal.getInstance(modal);
                bsModal.hide();
                // Sayfa yenile
                window.location.reload();
            } else {
                alert('Hata: ' + (data.message || 'Bilinmeyen hata'));
            }
        })
        .catch(err => alert('Sunucu hatası: ' + err));
    });
});
