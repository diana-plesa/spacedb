"""
Run with:  python manage.py test

Django creates a separate, empty test database for these tests,
so they never touch the data in db.sqlite3.
"""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Galaxy, StarSystem, Planet, BlackHole


class CrudTests(TestCase):
    def setUp(self):
        self.galaxy = Galaxy.objects.create(name='Milky Way', galaxy_type='spiral', distance_ly=26000,
                                            ra_deg=266.4, dec_deg=-29.0)
        self.system = StarSystem.objects.create(name='Solar System', galaxy=self.galaxy, distance_ly=0)

    def test_all_pages_load(self):
        planet = Planet.objects.create(name='Earth', system=self.system)
        for name in ['home', 'sky_map', 'galaxy_list', 'starsystem_list', 'star_list',
                     'planet_list', 'satellite_list', 'blackhole_list']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        for obj in [self.galaxy, self.system, planet]:
            self.assertEqual(self.client.get(obj.get_absolute_url()).status_code, 200)

    def test_create_planet(self):
        response = self.client.post(reverse('planet_create'), {
            'name': 'Mars', 'system': self.system.pk, 'mass_earth': '0.107',
        })
        mars = Planet.objects.get(name='Mars')
        self.assertRedirects(response, mars.get_absolute_url())

    def test_invalid_coordinates_are_rejected(self):
        response = self.client.post(reverse('galaxy_create'), {
            'name': 'Bad', 'galaxy_type': 'spiral', 'distance_ly': '1', 'ra_deg': '400',
        })
        self.assertEqual(response.status_code, 200)  # form shown again with an error
        self.assertFalse(Galaxy.objects.filter(name='Bad').exists())

    def test_quasar_needs_redshift(self):
        response = self.client.post(reverse('blackhole_create'), {
            'name': '3C 273', 'galaxy': self.galaxy.pk, 'bh_type': 'quasar',
        })
        self.assertContains(response, 'A quasar needs a redshift.')

    def test_deleting_galaxy_cascades(self):
        Planet.objects.create(name='Earth', system=self.system)
        self.client.post(reverse('galaxy_delete', args=[self.galaxy.pk]))
        self.assertEqual(StarSystem.objects.count(), 0)
        self.assertEqual(Planet.objects.count(), 0)


class JsonApiTests(TestCase):
    def setUp(self):
        galaxy = Galaxy.objects.create(name='Andromeda', galaxy_type='spiral', distance_ly=2537000,
                                       ra_deg=10.68, dec_deg=41.27)
        BlackHole.objects.create(name='M31*', galaxy=galaxy, bh_type='supermassive')  # no coordinates

    def test_search_finds_objects_of_any_type(self):
        data = self.client.get(reverse('api_search'), {'q': 'andro'}).json()
        self.assertEqual(data['results'][0]['name'], 'Andromeda')
        self.assertEqual(data['results'][0]['type'], 'Galaxy')

    def test_search_ignores_short_queries(self):
        data = self.client.get(reverse('api_search'), {'q': 'a'}).json()
        self.assertEqual(data['results'], [])

    def test_sky_objects_only_include_objects_with_coordinates(self):
        data = self.client.get(reverse('api_sky_objects')).json()
        self.assertEqual([obj['name'] for obj in data['objects']], ['Andromeda'])


class SeedCommandTests(TestCase):
    def test_seed_can_run_twice_without_duplicates(self):
        call_command('seed', stdout=StringIO())  # StringIO swallows the command's output
        count = Planet.objects.count()
        call_command('seed', stdout=StringIO())
        self.assertEqual(Planet.objects.count(), count)
        self.assertTrue(BlackHole.objects.filter(name='TON 618', bh_type='quasar').exists())
