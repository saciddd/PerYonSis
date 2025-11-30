/**
 * Vardiya Sayıları Hesaplama
 * Her gün için gündüz, akşam ve gece vardiyalarında kaç personel olduğunu gösterir
 */

let vardiyaTanimlari = {}; // Mesai tanım ID -> vardiya bilgileri

/**
 * Vardiya tanımlarını backend'den al
 */
function loadVardiyaTanimlari() {
    const url = window.urls?.vardiyaTanimlari;
    if (!url) {
        console.error('vardiyaTanimlari URL tanımlı değil!');
        return;
    }
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                vardiyaTanimlari = data.mesai_tanimlari || {};
                // Tanımlar yüklendikten sonra sayıları hesapla
                calculateVardiyaCounts();
            } else {
                console.error('Vardiya tanımları yüklenemedi:', data.message);
            }
        })
        .catch(error => {
            console.error('Vardiya tanımları yüklenirken hata:', error);
        });
}

/**
 * Mesai tanımının vardiya tipini döndürür
 */
function getVardiyaType(mesaiTanimId) {
    if (!mesaiTanimId) return null;
    
    const tanim = vardiyaTanimlari[mesaiTanimId];
    if (!tanim) return null;

    const types = [];
    if (tanim.gunduz) types.push('gunduz');
    if (tanim.aksam) types.push('aksam');
    if (tanim.gece) types.push('gece');
    
    return types.length > 0 ? types : null;
}

/**
 * Tüm günler için vardiya sayılarını hesapla
 */
function calculateVardiyaCounts() {
    if (!vardiyaTanimlari || Object.keys(vardiyaTanimlari).length === 0) {
        // Tanımlar henüz yüklenmediyse bekle
        setTimeout(calculateVardiyaCounts, 100);
        return;
    }

    // Tüm günleri bul
    const dayHeaders = document.querySelectorAll('thead tr:last-child th[class*="weekend"], thead tr:last-child th:not(.sticky-col):not([colspan])');
    const dayCells = Array.from(document.querySelectorAll('.mesai-cell[data-date]'));
    
    // Gün bazında sayıları hesapla
    const countsByDate = {};
    
    dayCells.forEach(cell => {
        const date = cell.getAttribute('data-date');
        if (!date) return;

        if (!countsByDate[date]) {
            countsByDate[date] = { gunduz: 0, aksam: 0, gece: 0 };
        }

        const mesaiId = cell.getAttribute('data-mesai-id');
        if (!mesaiId) return; // İzin veya boş hücre

        const vardiyaTypes = getVardiyaType(parseInt(mesaiId));
        if (vardiyaTypes) {
            vardiyaTypes.forEach(type => {
                countsByDate[date][type]++;
            });
        }
    });

    // Vardiya satırlarını güncelle
    Object.keys(countsByDate).forEach(date => {
        updateVardiyaCountForDay(date, countsByDate[date]);
    });
    
    // Renk skalasını uygula
    applyVardiyaColorScale();
}

/**
 * Belirli bir gün için vardiya sayılarını güncelle
 */
function updateVardiyaCountForDay(date, counts) {
    if (!counts) {
        // Sayıları yeniden hesapla
        const dayCells = document.querySelectorAll(`.mesai-cell[data-date="${date}"]`);
        counts = { gunduz: 0, aksam: 0, gece: 0 };
        
        dayCells.forEach(cell => {
            const mesaiId = cell.getAttribute('data-mesai-id');
            if (!mesaiId) return;

            const vardiyaTypes = getVardiyaType(parseInt(mesaiId));
            if (vardiyaTypes) {
                vardiyaTypes.forEach(type => {
                    counts[type]++;
                });
            }
        });
    }

    // Vardiya satırlarındaki ilgili hücreyi güncelle
    const vardiyaRows = {
        'gunduz': document.querySelector(`.gunduz-row th[data-date="${date}"]`),
        'aksam': document.querySelector(`.aksam-row th[data-date="${date}"]`),
        'gece': document.querySelector(`.gece-row th[data-date="${date}"]`)
    };

    if (vardiyaRows.gunduz) {
        vardiyaRows.gunduz.textContent = counts.gunduz || 0;
        vardiyaRows.gunduz.dataset.value = counts.gunduz || 0;
    }
    if (vardiyaRows.aksam) {
        vardiyaRows.aksam.textContent = counts.aksam || 0;
        vardiyaRows.aksam.dataset.value = counts.aksam || 0;
    }
    if (vardiyaRows.gece) {
        vardiyaRows.gece.textContent = counts.gece || 0;
        vardiyaRows.gece.dataset.value = counts.gece || 0;
    }
}

/**
 * Vardiya sayılarına göre renk skalası uygula
 */
function applyVardiyaColorScale() {
    const types = ['gunduz', 'aksam', 'gece'];
    let allCells = [];
    let allValues = [];

    // Tüm hücreleri ve değerleri topla
    types.forEach(type => {
        const cells = Array.from(document.querySelectorAll(`.${type}-row .vardiya-count`));
        cells.forEach(cell => {
            const value = parseInt(cell.dataset.value || cell.textContent || 0);
            allCells.push({ cell, value });
            allValues.push(value);
        });
    });

    if (allValues.length === 0) return;

    const min = Math.min(...allValues);
    const max = Math.max(...allValues);
    const range = max - min;

    allCells.forEach(({ cell, value }) => {
        if (range === 0) {
            // Hepsi aynıysa orta bir yeşil ver
            cell.style.backgroundColor = 'rgba(40, 167, 69, 0.3)'; 
            return;
        }
        
        // 0 (min) -> 0.1 alpha, 1 (max) -> 0.6 alpha
        const percentage = (value - min) / range;
        const alpha = 0.1 + (percentage * 0.5); 
        
        cell.style.backgroundColor = `rgba(40, 167, 69, ${alpha})`;
    });
}

/**
 * Mesai hücresi değiştiğinde vardiya sayılarını güncelle
 */
function updateVardiyaOnCellChange(cell) {
    const date = cell.getAttribute('data-date');
    if (!date) return;

    // Debounce ile güncelle
    if (window.vardiyaDebounceTimer) {
        clearTimeout(window.vardiyaDebounceTimer);
    }

    window.vardiyaDebounceTimer = setTimeout(() => {
        updateVardiyaCountForDay(date);
        applyVardiyaColorScale(); // Renkleri güncelle
    }, 300);
}

// Sayfa yüklendiğinde vardiya tanımlarını yükle
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadVardiyaTanimlari);
} else {
    loadVardiyaTanimlari();
}

