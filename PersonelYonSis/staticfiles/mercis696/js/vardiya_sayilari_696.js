/**
 * Vardiya Sayıları Hesaplama (Mercis 696)
 * Her gün için gündüz, akşam ve gece vardiyalarında kaç personel olduğunu gösterir
 */

let vardiyaTanimlari = {}; // Saat -> {gunduz: bool, aksam: bool, gece: bool}

/**
 * Vardiya tanımlarını sayfadan al (window.mesaiTanimlari)
 * ve hesaplamayı başlat
 */
function initVardiyaSayilari() {
    if (window.mesaiTanimlari) {
        vardiyaTanimlari = window.mesaiTanimlari;
        calculateVardiyaCounts();
    } else {
        console.warn('Vardiya tanımları bulunamadı!');
    }
}

/**
 * Mesai saatinin (text) vardiya tiplerini döndürür
 */
function getVardiyaTypes(saatText) {
    if (!saatText) return null;
    
    // Trim ve olası boşlukları temizle
    const key = saatText.trim();
    const tanim = vardiyaTanimlari[key];
    
    if (!tanim) return null;

    const types = [];
    // FileMaker'dan gelen verilerde 1 veya dolu olması true kabul edilir
    if (tanim.gunduz) types.push('gunduz');
    if (tanim.aksam) types.push('aksam');
    if (tanim.gece) types.push('gece');
    
    return types.length > 0 ? types : null;
}

/**
 * Tüm günler için vardiya sayılarını hesapla
 */
function calculateVardiyaCounts() {
    // Gün hücrelerini bul (header'daki data-date attribute'u olanlar)
    const dateHeaders = document.querySelectorAll('.vardiya-count[data-date]');
    const dates = Array.from(dateHeaders).map(th => th.getAttribute('data-date'));
    
    // Unique dates (sadece tarihleri al, gunduz/aksam/gece rowlari ayni tarihleri icerir)
    const uniqueDates = [...new Set(dates)];

    uniqueDates.forEach(date => {
        updateVardiyaCountForDay(date);
    });
}

/**
 * Belirli bir gün için vardiya sayılarını güncelle
 */
function updateVardiyaCountForDay(date) {
    const counts = { gunduz: 0, aksam: 0, gece: 0 };
    
    // O güne ait tüm veri hücrelerini bul
    // schedule_edit.html'de hücreler: td.mesai-cell[data-date="..."]
    const dayCells = document.querySelectorAll(`.mesai-cell[data-date="${date}"]`);
    
    dayCells.forEach(cell => {
        const text = cell.innerText.trim();
        if (!text || text === '--') return;

        const types = getVardiyaTypes(text);
        if (types) {
            types.forEach(type => {
                if (counts[type] !== undefined) {
                    counts[type]++;
                }
            });
        }
    });

    // Header hücrelerini güncelle
    const rows = ['gunduz', 'aksam', 'gece'];
    rows.forEach(type => {
        // İlgili satır ve tarihteki header hücresini bul
        // Selector: .vardiya-row.{type}-row .vardiya-count[data-date="{date}"]
        const headerCell = document.querySelector(`.vardiya-row.${type}-row .vardiya-count[data-date="${date}"]`);
        if (headerCell) {
            headerCell.textContent = counts[type];
            // Renklendirme için stil
            updateCellColor(headerCell, counts[type]);
        }
    });
}

function updateCellColor(cell, value) {
    if (value > 0) {
        // Basit bir yeşil tonlaması
        // Değer arttıkça koyulaşabilir veya sabit kalabilir, şimdilik sabit
        cell.style.backgroundColor = 'rgba(40, 167, 69, 0.2)';
        cell.style.color = 'black';
    } else {
        cell.style.backgroundColor = ''; // Reset
        cell.style.color = '';
    }
}

// Hücre değişikliklerini dinle
// schedule_edit.html'de zaten click handler var, oraya entegre edilebilir
// veya MutationObserver kullanılabilir. 
// Ancak schedule_edit.html'de $(this).text(newValue) yapılıyor.
// En temiz yöntem: bu fonksiyonu global'e açıp, schedule_edit.html'deki click handler içinden çağırmak.

// Global erişim için
window.updateVardiyaCountForDay = updateVardiyaCountForDay;
window.calculateVardiyaCounts = calculateVardiyaCounts;

// Sayfa yüklendiğinde başlat
$(document).ready(function() {
    initVardiyaSayilari();
});
