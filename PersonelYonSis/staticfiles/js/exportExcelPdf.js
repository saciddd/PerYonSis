// Excel export
document.getElementById('exportExcel').addEventListener('click', function () {
    let selectedYear = document.getElementById('selectYear').value;
    let selectedMonth = document.getElementById('selectMonth').value;

    // Excel dosyasını indirme
    window.location.href = `/export_excel/?year=${selectedYear}&month=${selectedMonth}`;
});

// PDF export
document.getElementById('exportPDF').addEventListener('click', function () {
    const year = document.getElementById('selectYear').value;
    const month = document.getElementById('selectMonth').value;

    const doc = new jsPDF();
    doc.text(`${year} - ${month} dönemi Mesai verileri`, 14, 16); // Başlık ekleme

    // Tabloyu almak
    var tableData = [];
    var rows = document.querySelectorAll('#cizelgeTable tbody tr');
    rows.forEach(row => {
        const rowData = [];
        const cells = row.querySelectorAll('td');
        cells.forEach(cell => {
            rowData.push(cell.innerText);
        });
        tableData.push(rowData);
    });

    // pdfmake ile tablo oluşturma
    doc.autoTable({
        head: [['Personel Adı', 'Personel Unvanı', 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]], // Başlıklar
        body: tableData,
        startY: 30 // Başlığın altından başlaması için
    });

    // PDF dosyasını indirme
    doc.save('mesai_verileri.pdf');
});
