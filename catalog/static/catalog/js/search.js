// Dynamic element 1: live search.
// While the user types, ask Django for matching objects (JSON) and show them
// in a dropdown under the search box, without reloading the page.
(function () {
    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    if (!input) return;

    let timer = null;
    let latestQuery = '';

    input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(runSearch, 200);  // wait until the user pauses typing
    });

    async function runSearch() {
        const query = input.value.trim();
        latestQuery = query;
        if (query.length < 2) {
            results.hidden = true;
            return;
        }
        const response = await fetch(input.dataset.url + '?q=' + encodeURIComponent(query));
        const data = await response.json();
        if (query !== latestQuery) return;  // the user kept typing; a newer search is on its way
        showResults(data.results);
    }

    function showResults(items) {
        results.innerHTML = '';
        if (items.length === 0) {
            const empty = document.createElement('li');
            empty.className = 'search-empty';
            empty.textContent = 'No matches';
            results.appendChild(empty);
        }
        for (const item of items) {
            // textContent (not innerHTML) so names are shown as text, never run as HTML
            const name = document.createElement('span');
            name.textContent = item.name;
            const type = document.createElement('span');
            type.className = 'search-type';
            type.textContent = item.type;

            const link = document.createElement('a');
            link.href = item.url;
            link.append(name, type);

            const li = document.createElement('li');
            li.appendChild(link);
            results.appendChild(li);
        }
        results.hidden = false;
    }

    // Enter opens the first result, Escape closes the dropdown
    input.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            const first = results.querySelector('a');
            if (first) window.location = first.href;
        } else if (event.key === 'Escape') {
            results.hidden = true;
            input.blur();
        }
    });

    // Clicking anywhere outside the search box closes the dropdown
    document.addEventListener('click', function (event) {
        if (!event.target.closest('.search')) results.hidden = true;
    });
})();
