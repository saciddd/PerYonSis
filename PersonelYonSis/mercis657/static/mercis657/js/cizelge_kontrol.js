/**
 * Çizelge Hata Kontrolü
 * Çeşitli kurallara göre çizelge hatalarını tespit eder
 */

let currentErrors = [];

/**
 * Tüm kontrolleri çalıştırır
 */
function checkCizelgeErrors() {
    // Önceki hataları temizle
    clearErrorMarkers();

    const errors = [];
    
    // 24 saatlik mesai sonrası kontrolü
    errors.push(...check24HourMesaiRule());
    
    // 5 gün boş bırakılmamalı kontrolü
    errors.push(...check5DayEmptyRule());

    currentErrors = errors;
    
    // Hataları işaretle
    markErrorCells(errors);

    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

/**
 * 24 saatlik mesai sonrası kontrolü
 */
function check24HourMesaiRule() {
    const errors = [];
    const cells = document.querySelectorAll('.mesai-cell[data-mesai-id]');

    cells.forEach(cell => {
        const mesaiId = cell.getAttribute('data-mesai-id');
        const date = cell.getAttribute('data-date');
        const personelId = cell.getAttribute('data-personel-id');

        if (!mesaiId || !date || !personelId) return;

        // Mesai tanımını kontrol et (DOM'dan veya backend'den)
        // Basitleştirilmiş: SonrakiGuneSarkiyor ve Sure >= 24 kontrolü için
        // Backend'den mesai tanım bilgilerini almak gerekebilir
        // Şimdilik sadece DOM'daki verilerle çalışıyoruz

        // Sonraki günü bul
        const currentDate = new Date(date);
        currentDate.setDate(currentDate.getDate() + 1);
        const nextDateStr = currentDate.toISOString().split('T')[0];

        // Sonraki günün hücresini bul
        const nextCell = document.querySelector(
            `.mesai-cell[data-date="${nextDateStr}"][data-personel-id="${personelId}"]`
        );

        if (nextCell) {
            const nextMesaiId = nextCell.getAttribute('data-mesai-id');
            const nextIzinId = nextCell.getAttribute('data-izin-id');

            // Eğer sonraki günde mesai varsa ve izin değilse hata
            if (nextMesaiId && !nextIzinId) {
                // Not: 24 saatlik ve SonrakiGuneSarkiyor kontrolü için
                // backend'den mesai tanım bilgilerini almak gerekir
                // Şimdilik bu kontrolü backend'e bırakıyoruz
            }
        }
    });

    return errors;
}

/**
 * 5 gün boş bırakılmamalı kontrolü
 */
function check5DayEmptyRule() {
    const errors = [];
    const personelRows = document.querySelectorAll('tr[id^="personel-"]');

    personelRows.forEach(row => {
        const personelId = row.id.match(/personel-(\d+)/)?.[1];
        if (!personelId) return;

        const personelName = row.querySelector('.sticky-col-2')?.textContent?.trim() || 'Bilinmeyen';
        const cells = row.querySelectorAll('.mesai-cell[data-date]');

        // Tarihleri sırala
        const dates = Array.from(cells).map(cell => ({
            date: cell.getAttribute('data-date'),
            cell: cell,
            hasData: cell.getAttribute('data-mesai-id') || cell.getAttribute('data-izin-id')
        })).sort((a, b) => a.date.localeCompare(b.date));

        // Ardışık boş günleri kontrol et
        let consecutiveEmpty = 0;
        let emptyStart = null;
        let lastDate = null;

        dates.forEach((item, index) => {
            const currentDate = new Date(item.date);
            const weekday = currentDate.getDay(); // 0=Pazar, 6=Cumartesi
            
            // Hafta sonu kontrolü (basitleştirilmiş)
            const isWeekend = weekday === 0 || weekday === 6;

            if (!isWeekend) {
                if (!item.hasData) {
                    if (consecutiveEmpty === 0) {
                        emptyStart = item.date;
                    }
                    consecutiveEmpty++;
                } else {
                    if (consecutiveEmpty >= 5) {
                        errors.push({
                            type: '5_day_empty',
                            message: `${personelName} için ${emptyStart} - ${lastDate || item.date} arası ${consecutiveEmpty} gün boyunca mesai verisi yok`,
                            personel_id: personelId,
                            date: emptyStart,
                            cell_selector: `td[data-date="${emptyStart}"][data-personel-id="${personelId}"]`
                        });
                    }
                    consecutiveEmpty = 0;
                    emptyStart = null;
                }
                lastDate = item.date;
            }
        });

        // Son kontrol: Eğer ay sonunda hala boş günler varsa
        if (consecutiveEmpty >= 5) {
            errors.push({
                type: '5_day_empty',
                message: `${personelName} için ${emptyStart} - ${lastDate} arası ${consecutiveEmpty} gün boyunca mesai verisi yok`,
                personel_id: personelId,
                date: emptyStart,
                cell_selector: `td[data-date="${emptyStart}"][data-personel-id="${personelId}"]`
            });
        }
    });

    return errors;
}

/**
 * Hatalı hücreleri görsel olarak işaretle
 */
function markErrorCells(errors) {
    errors.forEach(error => {
        if (!error.cell_selector) return;

        const cell = document.querySelector(error.cell_selector);
        if (cell) {
            cell.classList.add('error-cell');
            
            // Uyarı ikonu ekle (eğer yoksa)
            if (!cell.querySelector('.warning-icon')) {
                const icon = document.createElement('i');
                icon.className = 'bi bi-exclamation-triangle-fill warning-icon';
                icon.style.color = '#dc3545';
                icon.style.fontSize = '0.9em';
                icon.style.marginRight = '4px';
                icon.title = error.message;
                cell.insertBefore(icon, cell.firstChild);
            }
        }
    });
}

/**
 * Hata işaretlerini temizle
 */
function clearErrorMarkers() {
    // Önceki uyarı ikonlarını temizle
    document.querySelectorAll('.warning-icon').forEach(icon => icon.remove());
    
    // Error-cell class'ını kaldır
    document.querySelectorAll('.error-cell').forEach(cell => {
        cell.classList.remove('error-cell');
    });
}

/**
 * Backend'den hata kontrolü yap (daha güvenilir)
 */
function checkCizelgeErrorsBackend() {
    const donem = document.getElementById('selectDonem')?.value;
    if (!donem) {
        Swal.fire('Uyarı', 'Lütfen dönem seçiniz.', 'warning');
        return;
    }

    const [year, month] = donem.split('/');
    const listeId = window.listeId || document.getElementById('selectBirim')?.value;

    if (!listeId) {
        Swal.fire('Uyarı', 'Liste bulunamadı.', 'warning');
        return;
    }

    // Loading göster
    Swal.fire({
        title: 'Kontrol ediliyor...',
        html: 'Hatalar tespit ediliyor, lütfen bekleyin.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    const url = window.urls?.cizelgeKontrol;
    if (!url) {
        Swal.fire('Hata', 'cizelgeKontrol URL tanımlı değil!', 'error');
        return;
    }
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            liste_id: parseInt(listeId),
            year: parseInt(year),
            month: parseInt(month)
        })
    })
    .then(response => response.json())
    .then(data => {
        Swal.close();
        
        if (data.status === "success") {
            const errors = data.errors || [];
            currentErrors = errors;
            
            // Önceki işaretleri temizle
            clearErrorMarkers();

            // Hataları işaretle
            markErrorCells(errors);

            if (errors.length === 0) {
                Swal.fire({
                    title: 'Kontrol Tamamlandı',
                    text: 'Tüm kayıtlar tutarlı!',
                    icon: 'success',
                    confirmButtonText: 'Tamam'
                });
            } else {
                // Hata ve bilgi mesajlarını ayır
                const realErrors = errors.filter(e => e.type !== 'info');
                const infoMessages = errors.filter(e => e.type === 'info');
                
                let title = 'Hata Tespit Edildi';
                let icon = 'warning';
                
                if (realErrors.length === 0 && infoMessages.length > 0) {
                    title = 'Bilgilendirme';
                    icon = 'info';
                } else if (realErrors.length > 0 && infoMessages.length > 0) {
                    title = 'Hata ve Bilgilendirme';
                }

                const messagesHtml = errors.map(e => {
                    const color = e.type === 'info' ? 'text-primary' : 'text-danger';
                    const icon = e.type === 'info' ? '<i class="bi bi-info-circle me-2"></i>' : '<i class="bi bi-exclamation-triangle me-2"></i>';
                    return `<div class="${color} mb-2" style="font-size: 0.95rem;">${icon}${e.message}</div>`;
                }).join('');

                // initializeFazlaMesaiCalculation fonksiyonunu tekrar çalıştır
                initializeFazlaMesaiCalculation();

                Swal.fire({
                    title: title,
                    html: `<div class="text-start">${messagesHtml}</div>`,
                    icon: icon,
                    confirmButtonText: 'Tamam'
                });
            }
        } else {
            Swal.fire({
                title: 'Hata',
                text: data.message || 'Kontrol sırasında bir hata oluştu.',
                icon: 'error'
            });
        }
    })
    .catch(error => {
        Swal.close();
        console.error('Hata kontrolü hatası:', error);
        Swal.fire({
            title: 'Hata',
            text: 'Kontrol sırasında bir hata oluştu.',
            icon: 'error'
        });
    });
}

// Hata Kontrolü butonuna event listener ekle
document.addEventListener('DOMContentLoaded', function() {
    const hataKontrolBtn = document.getElementById('hataKontrolBtn');
    if (hataKontrolBtn) {
        hataKontrolBtn.addEventListener('click', function() {
            // Backend kontrolü kullan (daha güvenilir)
            checkCizelgeErrorsBackend();
        });
    }
});

