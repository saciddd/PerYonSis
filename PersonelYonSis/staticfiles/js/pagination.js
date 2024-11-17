function paginateTable(pageSize) {
    var table = document.getElementById('cizelgeTable');
    var rows = Array.from(table.querySelectorAll('tbody tr'));
    var currentPage = 1;

    function displayRows() {
        rows.forEach(function (row, index) {
            row.style.display = (index >= (currentPage - 1) * pageSize && index < currentPage * pageSize) ? '' : 'none';
        });
    }

    displayRows();

    // Var olan pagination div'ini temizle
    var oldPagination = document.querySelector('.pagination');
    if (oldPagination) {
        oldPagination.remove();
    }

    var pagination = document.createElement('div');
    pagination.classList.add('pagination');

    for (var i = 1; i <= Math.ceil(rows.length / pageSize); i++) {
        var button = document.createElement('button');
        button.textContent = i;
        button.addEventListener('click', function () {
            currentPage = +this.textContent;
            displayRows();
        });
        pagination.appendChild(button);
    }

    table.parentNode.appendChild(pagination);
}

// 7 satırlık pagination örneği
paginateTable(7);
