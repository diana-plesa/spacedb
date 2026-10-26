// Dynamic element 3: interactive sky map.
// Aladin Lite (from the CDS in Strasbourg) shows a real survey of the sky. We load our
// objects from Django's JSON endpoint and draw each type as its own layer.
// Every layer uses the site's accent color; the marker shape tells the types apart.
const MARKER_COLOR = '#e4572e';
const LAYER_SHAPES = {
    galaxy: { shape: 'circle', symbol: '○' },
    starsystem: { shape: 'rhomb', symbol: '◇' },
    star: { shape: 'plus', symbol: '+' },
    planet: { shape: 'square', symbol: '□' },
    satellite: { shape: 'cross', symbol: '×' },
    blackhole: { shape: 'triangle', symbol: '△' },
};

const mapDiv = document.getElementById('aladin-lite-div');

if (typeof A === 'undefined') {
    mapDiv.textContent = 'Could not load Aladin Lite. Check your internet connection and reload.';
} else {
    A.init.then(setUpMap);
}

async function setUpMap() {
    // /sky/?ra=10.68&dec=41.27 opens the map zoomed in on that point
    const params = new URLSearchParams(window.location.search);
    const hasTarget = params.has('ra') && params.has('dec');

    const aladin = A.aladin('#aladin-lite-div', {
        survey: 'P/DSS2/color',
        projection: hasTarget ? 'SIN' : 'AIT',  // AIT shows the whole sky as an ellipse
        fov: hasTarget ? 3 : 360,
        target: hasTarget ? params.get('ra') + ' ' + params.get('dec') : '0 0',
        cooFrame: 'J2000',
    });

    const response = await fetch(mapDiv.dataset.url);
    const data = await response.json();

    // One Aladin catalog (layer) per object type
    const layers = {};
    for (const obj of data.objects) {
        if (!layers[obj.kind]) {
            const catalog = A.catalog({
                name: obj.kind_label_plural,
                color: MARKER_COLOR,
                sourceSize: 16,
                shape: LAYER_SHAPES[obj.kind].shape,
            });
            aladin.addCatalog(catalog);
            layers[obj.kind] = { catalog: catalog, label: obj.kind_label_plural, count: 0 };
        }
        // The third argument is our own data; Aladin gives it back when the source is clicked
        layers[obj.kind].catalog.addSources([A.source(obj.ra, obj.dec, obj)]);
        layers[obj.kind].count++;
    }

    buildLayerToggles(layers);
    buildObjectList(aladin, data.objects);

    aladin.on('objectClicked', function (source) {
        if (source && source.data && source.data.url) showInfo(source.data);
    });
}

function buildLayerToggles(layers) {
    const container = document.getElementById('sky-layers');
    for (const kind in layers) {
        const layer = layers[kind];
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = true;
        checkbox.addEventListener('change', function () {
            if (checkbox.checked) layer.catalog.show();
            else layer.catalog.hide();
        });

        const swatch = document.createElement('span');
        swatch.className = 'swatch';
        swatch.textContent = LAYER_SHAPES[kind].symbol;

        const label = document.createElement('label');
        label.className = 'layer-toggle';
        label.append(checkbox, swatch, layer.label + ' (' + layer.count + ')');
        container.appendChild(label);
    }
    if (container.children.length === 0) {
        container.textContent = 'No objects have coordinates yet.';
    }
}

function buildObjectList(aladin, objects) {
    const list = document.getElementById('sky-object-list');
    for (const obj of objects) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'sky-object';
        button.textContent = LAYER_SHAPES[obj.kind].symbol + '  ' + obj.name;
        button.addEventListener('click', function () {
            aladin.setProjection('SIN');
            aladin.gotoRaDec(obj.ra, obj.dec);
            aladin.setFoV(3);
            showInfo(obj);
        });

        const li = document.createElement('li');
        li.appendChild(button);
        list.appendChild(li);
    }
}

function showInfo(obj) {
    const image = document.getElementById('sky-info-image');
    image.hidden = !obj.image_url;
    if (obj.image_url) image.src = obj.image_url;
    document.getElementById('sky-info-name').textContent = obj.name;
    document.getElementById('sky-info-type').textContent = obj.kind_label;
    document.getElementById('sky-info-coords').textContent =
        'RA ' + obj.ra.toFixed(4) + '°, Dec ' + obj.dec.toFixed(4) + '°';
    document.getElementById('sky-info-link').href = obj.url;
    document.getElementById('sky-info').hidden = false;
}
