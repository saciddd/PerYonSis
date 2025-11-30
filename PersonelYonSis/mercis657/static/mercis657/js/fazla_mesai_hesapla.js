/**
 * Anlık Fazla Mesai Hesaplama
 * Sayfa yüklendiğinde ve mesai hücresi değiştiğinde fazla mesai değerlerini günceller
 */

// Cache ve debounce için
let fazlaMesaiCache = {};
let fazlaMesaiDebounceTimer = null;
const DEBOUNCE_DELAY = 500; // ms

/**
 * Fazla mesai hücresini güncelle
 */
function updateFazlaMesaiCell(personelId, fazlaMesai) {
    const rowId = `personel-${personelId}`;
    const cell = document.querySelector(`#${rowId} .fazla-mesai-cell`);
    if (cell) {
        const fm = Number(fazlaMesai);
        cell.textContent = `${fm > 0 ? '+' : ''}${fm}`;
        cell.classList.remove('fm-pos', 'fm-neg');
        if (fm > 0) {
            cell.classList.add('fm-pos');
        } else if (fm < 0) {
            cell.classList.add('fm-neg');
        }
    }
}

/**
 * Mesai hücresi değiştiğinde fazla mesaiyi güncelle (debounce ile)
 */
function updateFazlaMesaiOnCellChange(cell) {
    const personelId = cell.getAttribute('data-personel-id');
    if (!personelId) return;

    // Dönem bilgisini al
    const donem = document.getElementById('selectDonem')?.value;
    if (!donem) return;

    const [year, month] = donem.split('/');
    // Liste ID'yi window.listeId'den al, yoksa birim seçiminden al
    let listeId = (window.listeId && window.listeId !== 0) ? window.listeId : null;
    if (!listeId) {
        const birimSelect = document.getElementById('selectBirim');
        if (birimSelect) listeId = birimSelect.value;
    }

    // Debounce: Önceki timer'ı iptal et
    if (fazlaMesaiDebounceTimer) {
        clearTimeout(fazlaMesaiDebounceTimer);
    }

    // Yeni timer başlat
    fazlaMesaiDebounceTimer = setTimeout(() => {
        calculateFazlaMesaiForPersonel(parseInt(personelId), parseInt(year), parseInt(month), listeId);
    }, DEBOUNCE_DELAY);
}

/**
 * Sayfa yüklendiğinde tüm personeller için fazla mesai hesapla
 */
function initializeFazlaMesaiCalculation() {
    const donem = document.getElementById('selectDonem')?.value;
    if (!donem) return;

    const [year, month] = donem.split('/');
    // Liste ID'yi window.listeId'den al, yoksa birim seçiminden al
    let listeId = (window.listeId && window.listeId !== 0) ? window.listeId : null;
    if (!listeId) {
        const birimSelect = document.getElementById('selectBirim');
        if (birimSelect) listeId = birimSelect.value;
    }

    if (!listeId) {
        console.warn('Liste ID bulunamadı, toplu hesaplama yapılamıyor');
        return;
    }

    // Tüm personel satırlarını bul
    const personelRows = document.querySelectorAll('tr[id^="personel-"]');
    const personelIds = Array.from(personelRows).map(row => {
        const match = row.id.match(/personel-(\d+)/);
        return match ? parseInt(match[1]) : null;
    }).filter(id => id !== null);

    if (personelIds.length === 0) return;

    // Toplu hesaplama için backend'e istek gönder
    const topluUrl = window.urls?.fazlaMesaiToplu;
    if (!topluUrl) {
        console.error('fazlaMesaiToplu URL tanımlı değil!');
        return;
    }
    fetch(topluUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            personel_ids: personelIds,
            year: parseInt(year),
            month: parseInt(month),
            liste_id: parseInt(listeId)
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                data.data.forEach(item => {
                    updateFazlaMesaiCell(item.personel_id, item.fazla_mesai);
                    // Cache'e kaydet
                    const cacheKey = `${item.personel_id}_${year}_${month}`;
                    fazlaMesaiCache[cacheKey] = {
                        value: item.fazla_mesai,
                        timestamp: Date.now()
                    };
                });
            } else {
                console.error('Toplu fazla mesai hesaplama hatası:', data.message);
            }
        })
        .catch(error => {
            console.error('Toplu fazla mesai hesaplama hatası:', error);
        });
}

// Sayfa yüklendiğinde çalıştır
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeFazlaMesaiCalculation);
} else {
    initializeFazlaMesaiCalculation();
}

