// On the black hole form, show the luminosity and redshift fields only when the type is Quasar.
// (The server also clears them for other types, so this is just to keep the form tidy.)
(function () {
    const typeSelect = document.getElementById('id_bh_type');
    if (!typeSelect) return;

    // form.as_p wraps each field (label, input, help text) in a <p>
    const quasarRows = ['id_luminosity_solar', 'id_redshift']
        .map(id => document.getElementById(id).closest('p'));

    function update() {
        for (const row of quasarRows) row.hidden = typeSelect.value !== 'quasar';
    }

    typeSelect.addEventListener('change', update);
    update();
})();
