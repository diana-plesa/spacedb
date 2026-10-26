// Dynamic element 2: filter and sort the table on list pages, without reloading.
// Works on any table with class "js-table":
//   - a text box filters rows by any text they contain
//   - a dropdown filters by the row's data-category (filled from the rows themselves)
//   - clicking a column header with data-sort="text" or "number" sorts by that column
(function () {
    const table = document.querySelector('.js-table');
    if (!table) return;

    const filterInput = document.querySelector('.toolbar-filter');
    const categorySelect = document.querySelector('.toolbar-category');
    const countLabel = document.querySelector('.toolbar-count');
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.rows);

    // A row shown when nothing matches the filters
    const noMatchesRow = document.createElement('tr');
    const noMatchesCell = document.createElement('td');
    noMatchesCell.colSpan = table.tHead.rows[0].cells.length;
    noMatchesCell.className = 'muted';
    noMatchesCell.textContent = 'No matches.';
    noMatchesRow.appendChild(noMatchesCell);
    noMatchesRow.hidden = true;
    tbody.appendChild(noMatchesRow);

    // ----- Filtering -----

    const categories = [...new Set(rows.map(row => row.dataset.category).filter(Boolean))].sort();
    for (const category of categories) {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        categorySelect.appendChild(option);
    }
    categorySelect.hidden = categories.length < 2;

    function applyFilters() {
        const text = filterInput.value.trim().toLowerCase();
        const category = categorySelect.value;
        let shown = 0;
        for (const row of rows) {
            const matchesText = row.textContent.toLowerCase().includes(text);
            const matchesCategory = category === '' || row.dataset.category === category;
            row.hidden = !(matchesText && matchesCategory);
            if (!row.hidden) shown++;
        }
        countLabel.textContent = shown + ' of ' + rows.length + ' shown';
        noMatchesRow.hidden = shown > 0;
    }

    filterInput.addEventListener('input', applyFilters);
    categorySelect.addEventListener('change', applyFilters);
    applyFilters();

    // ----- Sorting -----

    function cellValue(row, columnIndex, isNumber) {
        const text = row.cells[columnIndex].textContent.trim();
        if (!isNumber) return text.toLowerCase();
        const number = parseFloat(text.replace(/[^0-9.\-]/g, ''));  // "2,537,000" -> 2537000
        return isNaN(number) ? null : number;                        // "—" (no value) -> null
    }

    function sortBy(header) {
        const columnIndex = header.cellIndex;
        const isNumber = header.dataset.sort === 'number';
        const ascending = header.dataset.direction !== 'asc';  // clicking again flips the order

        for (const other of table.tHead.rows[0].cells) delete other.dataset.direction;
        header.dataset.direction = ascending ? 'asc' : 'desc';

        rows.sort(function (a, b) {
            const x = cellValue(a, columnIndex, isNumber);
            const y = cellValue(b, columnIndex, isNumber);
            if (x === y) return 0;
            if (x === null) return 1;   // empty values always go last
            if (y === null) return -1;
            const result = isNumber ? x - y : x.localeCompare(y);
            return ascending ? result : -result;
        });

        // Re-appending existing rows moves them, so this reorders the table
        for (const row of rows) tbody.appendChild(row);
        tbody.appendChild(noMatchesRow);
    }

    for (const header of table.querySelectorAll('th[data-sort]')) {
        header.classList.add('sortable');
        header.title = 'Click to sort';
        header.addEventListener('click', () => sortBy(header));
    }
})();
