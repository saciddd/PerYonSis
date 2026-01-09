/**
 * Excel Export Helper using SheetJS
 * This script provides functionality to export HTML tables to Excel files (.xlsx).
 * It requires the SheetJS library (xlsx.full.min.js) to be loaded before usage.
 */

const ExcelExport = {
    /**
     * Checks if the required library is loaded.
     */
    checkLibrary: function() {
        if (typeof XLSX === 'undefined') {
            alert('Excel dışa aktarma kütüphanesi (SheetJS) yüklenemedi. Lütfen internet bağlantınızı kontrol edip sayfayı yenileyiniz.');
            return false;
        }
        return true;
    },

    /**
     * Exports an HTML table to an Excel file.
     * @param {string|HTMLElement} sourceElement - The ID of the container/table or the HTMLElement itself.
     * @param {string} filename - The name of the file to be saved (without extension is fine).
     * @param {string} sheetName - Optional name for the worksheet.
     */
    exportTable: function(sourceElement, filename, sheetName = 'Sayfa1') {
        if (!this.checkLibrary()) return;

        let table = null;
        if (typeof sourceElement === 'string') {
            const el = document.getElementById(sourceElement);
            if (el) {
                table = el.tagName === 'TABLE' ? el : el.querySelector('table');
            }
        } else if (sourceElement instanceof HTMLElement) {
            table = sourceElement.tagName === 'TABLE' ? sourceElement : sourceElement.querySelector('table');
        }

        if (!table) {
            console.error('ExcelExport: Tablo bulunamadı ->', sourceElement);
            alert('Dışa aktarılacak tablo verisi bulunamadı.');
            return;
        }

        try {
            // Create a new workbook
            const wb = XLSX.utils.book_new();
            
            // Convert table to worksheet
            // raw: true helps in keeping numbers as numbers, dates as dates if parsed correctly.
            const ws = XLSX.utils.table_to_sheet(table, { raw: true });

            // Append worksheet to workbook
            XLSX.utils.book_append_sheet(wb, ws, sheetName);

            // Generate Excel file
            const fullFilename = filename.endsWith('.xlsx') ? filename : filename + '.xlsx';
            XLSX.writeFile(wb, fullFilename);
        } catch (error) {
            console.error('ExcelExport Error:', error);
            alert('Excel dosyası oluşturulurken bir hata meydana geldi: ' + error.message);
        }
    }
};

// Global helper specifically for the modal interaction if needed globally
// But keeping it generic is better.
