document.getElementById('searchInput').addEventListener('input', function () {
    var filter = this.value.toUpperCase();
    var rows = document.querySelectorAll('#cizelgeTable tbody tr');

    rows.forEach(function (row) {
        var match = Array.from(row.cells).some(function (cell) {
            return cell.textContent.toUpperCase().indexOf(filter) > -1;
        });
        row.style.display = match ? '' : 'none';
    });
});

function sortTable(n) {
    var table = document.getElementById("cizelgeTable");
    var rows = Array.from(table.rows).slice(1);
    var asc = true;

    rows.sort(function (rowA, rowB) {
        var cellA = rowA.cells[n].textContent.toUpperCase();
        var cellB = rowB.cells[n].textContent.toUpperCase();
        return asc ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
    });

    asc = !asc;
    rows.forEach(function (row) {
        table.tBodies[0].appendChild(row);
    });
}