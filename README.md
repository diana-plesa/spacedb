# spacedb

A database website for objects in space (galaxies, star systems, stars, planets and exoplanets, natural and artificial satellites, and black holes including quasars), built with Django.

It comes with real data (TRAPPIST-1's seven planets, Proxima Centauri b, Sagittarius A\*, M87\*, the quasars 3C 273 and TON 618, and more) and an interactive sky map that plots every object at its true position in the sky.

## Features

- **Full CRUD** for six related models: create, view, edit and delete, with validation. Coordinates must be in range, and a quasar needs a redshift.
- **Cascade-aware deletes.** Before deleting something, the confirmation page lists everything that will be deleted along with it (for example, a galaxy's star systems, their planets, and those planets' moons).
- **Live search** across all object types from the navigation bar, using a JSON endpoint and `fetch`.
- **Instant filtering and sorting** on every list page, without reloading.
- **Interactive sky map** built on [Aladin Lite](https://aladin.cds.unistra.fr/AladinLite/) over a real sky survey (DSS2). It has toggleable layers per object type, a click-to-fly object list, and a "View on sky map" link on every detail page.
- Pictures from Wikimedia Commons for every seeded object, each credited with a link to its source page. You can add your own picture to any object through its form.
- Django admin for all models, including inline editing of a star system's stars and planets.
- A hand-made "old star atlas" design with no CSS framework: two typefaces (Fraunces and IBM Plex Mono), three colors, and a responsive layout.
- Automated tests for the pages, forms, JSON endpoints and seed command.

## Tech stack

Python 3.11, Django 5.2, SQLite, vanilla JavaScript (`fetch`, the DOM API), Aladin Lite v3, and plain CSS.

## Running it locally (Windows / PowerShell)

```powershell
git clone <repo-url>
cd space_app
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed              # loads the real astronomical data
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Then open http://127.0.0.1:8000/. On macOS or Linux, activate the virtual environment with `source venv/bin/activate` instead.

Run the tests with `python manage.py test`.

## Data model

```
Galaxy ─┬─< StarSystem ─┬─< Star
        │               └─< Planet ──< Satellite
        └─< BlackHole
```

All six models inherit from an abstract base class, `CelestialObject`, which provides `name`, `description`, and sky coordinates (`ra_deg`, `dec_deg`). Each relation uses `on_delete=CASCADE` and a `related_name` (for example, `galaxy.star_systems.all()`).

## JSON endpoints

| URL | Returns |
|---|---|
| `/api/search/?q=<text>` | Objects of any type whose name contains the text (at least 2 characters), each with `name`, `type` and `url` |
| `/api/sky-objects/` | Every object that has coordinates, with `name`, `kind`, `ra`, `dec` and `url` |

## Project structure

```
spacedb/                     project settings and root URLs
catalog/
    models.py                CelestialObject base class and the six models
    views.py                 class-based CRUD views and the JSON endpoints
    forms.py                 one ModelForm per model, plus cross-field validation
    urls.py
    admin.py
    tests.py
    management/commands/seed.py      python manage.py seed
    templates/catalog/       base layout, per-model list/detail pages, shared form/delete pages
    static/catalog/
        css/style.css
        js/search.js         live search
        js/table-tools.js    filtering and sorting on list pages
        js/sky-map.js        Aladin Lite sky map
```

## Data sources

The seed data uses rounded published values from NASA, ESA, the NASA Exoplanet Archive and SIMBAD. Coordinates are J2000 right ascension and declination in degrees. Pictures are loaded directly from Wikimedia Commons; each picture's author and licence are on the source page linked under it.
