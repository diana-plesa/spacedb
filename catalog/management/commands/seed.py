"""
Fills the database with real astronomical objects.

Run with:  python manage.py seed

Safe to run more than once: objects are matched by name, and for objects that
already exist only empty fields are filled in, so your own edits are kept.
Values are rounded, published figures (NASA, ESA, NASA Exoplanet Archive, SIMBAD).
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Galaxy, StarSystem, Star, Planet, Satellite, BlackHole


def upsert(model, name, **fields):
    obj, created = model.objects.get_or_create(name=name, defaults=fields)
    if not created:
        for field, value in fields.items():
            if getattr(obj, field) in (None, ''):
                setattr(obj, field, value)
        obj.save()
    return obj


class Command(BaseCommand):
    help = 'Adds real galaxies, star systems, stars, planets, satellites and black holes.'

    @transaction.atomic  # all or nothing: if anything fails, nothing is saved
    def handle(self, *args, **options):
        # ---------- Galaxies ----------
        milky_way = upsert(
            Galaxy, 'Milky Way', galaxy_type='spiral', distance_ly=26000,
            ra_deg=266.4168, dec_deg=-29.0078,
            description='Our home galaxy, a barred spiral about 100,000 light-years across. '
                        'Distance and coordinates are those of the galactic centre.')
        andromeda = upsert(
            Galaxy, 'Andromeda', galaxy_type='spiral', distance_ly=2537000,
            ra_deg=10.6847, dec_deg=41.2690,
            description='The nearest large galaxy to the Milky Way and the most distant object '
                        'visible to the naked eye. It will merge with the Milky Way in about 4.5 billion years.')
        upsert(Galaxy, 'Triangulum Galaxy', galaxy_type='spiral', distance_ly=2730000,
               ra_deg=23.4621, dec_deg=30.6599,
               description='The third-largest member of the Local Group (Messier 33).')
        upsert(Galaxy, 'Large Magellanic Cloud', galaxy_type='irregular', distance_ly=163000,
               ra_deg=80.8942, dec_deg=-69.7561,
               description='A satellite galaxy of the Milky Way, visible from the southern hemisphere.')
        upsert(Galaxy, 'Small Magellanic Cloud', galaxy_type='irregular', distance_ly=200000,
               ra_deg=13.1867, dec_deg=-72.8286,
               description='A dwarf irregular galaxy orbiting the Milky Way.')
        upsert(Galaxy, 'Whirlpool Galaxy', galaxy_type='spiral', distance_ly=23000000,
               ra_deg=202.4696, dec_deg=47.1952,
               description='A classic face-on spiral (Messier 51) interacting with a smaller companion.')
        m87 = upsert(
            Galaxy, 'Messier 87', galaxy_type='elliptical', distance_ly=53500000,
            ra_deg=187.7059, dec_deg=12.3911,
            description='A supergiant elliptical galaxy in the Virgo Cluster, with a jet of '
                        'plasma shooting out of its core.')
        centaurus_a = upsert(
            Galaxy, 'Centaurus A', galaxy_type='lenticular', distance_ly=12000000,
            ra_deg=201.3651, dec_deg=-43.0191,
            description='A peculiar lenticular galaxy crossed by a dark dust lane; one of the '
                        'brightest radio sources in the sky.')
        host_3c273 = upsert(
            Galaxy, '3C 273 host galaxy', galaxy_type='elliptical', distance_ly=2443000000,
            ra_deg=187.2779, dec_deg=2.0524,
            description='The giant elliptical galaxy that hosts quasar 3C 273.')
        host_ton618 = upsert(
            Galaxy, 'TON 618 host galaxy', galaxy_type='elliptical', distance_ly=10800000000,
            ra_deg=187.1038, dec_deg=31.4772,
            description='The distant galaxy that hosts the hyperluminous quasar TON 618 '
                        '(distance given as light-travel distance).')

        # ---------- The Solar System ----------
        solar = upsert(StarSystem, 'Solar System', galaxy=milky_way, distance_ly=0,
                       description='The Sun and everything bound to it by gravity.')
        upsert(Star, 'Sun', system=solar, spectral_type='G2V', mass_solar=1, temperature_k=5772)

        planets = {}
        for name, mass, radius, period in [
            ('Mercury', 0.0553, 0.383, 87.97),
            ('Venus', 0.815, 0.949, 224.70),
            ('Earth', 1.0, 1.0, 365.26),
            ('Mars', 0.107, 0.532, 686.98),
            ('Jupiter', 317.8, 11.21, 4332.59),
            ('Saturn', 95.2, 9.45, 10759.22),
            ('Uranus', 14.5, 4.01, 30688.5),
            ('Neptune', 17.1, 3.88, 60195.0),
        ]:
            planets[name] = upsert(Planet, name, system=solar, mass_earth=mass, radius_earth=radius,
                                   orbital_period_days=period, is_exoplanet=False)

        for name, planet, kind in [
            ('Moon', 'Earth', 'natural'),
            ('International Space Station', 'Earth', 'artificial'),
            ('Hubble Space Telescope', 'Earth', 'artificial'),
            ('Phobos', 'Mars', 'natural'),
            ('Deimos', 'Mars', 'natural'),
            ('Io', 'Jupiter', 'natural'),
            ('Europa', 'Jupiter', 'natural'),
            ('Ganymede', 'Jupiter', 'natural'),
            ('Callisto', 'Jupiter', 'natural'),
            ('Titan', 'Saturn', 'natural'),
            ('Enceladus', 'Saturn', 'natural'),
            ('Triton', 'Neptune', 'natural'),
        ]:
            upsert(Satellite, name, planet=planets[planet], kind=kind)

        # ---------- Nearby star systems with exoplanets ----------
        alpha_cen = upsert(
            StarSystem, 'Alpha Centauri', galaxy=milky_way, distance_ly=4.37,
            ra_deg=219.9021, dec_deg=-60.8340,
            description='The closest star system to the Sun: a triple system of two Sun-like stars and the red dwarf Proxima.')
        upsert(Star, 'Alpha Centauri A', system=alpha_cen, spectral_type='G2V', mass_solar=1.08,
               temperature_k=5790, ra_deg=219.9021, dec_deg=-60.8340)
        upsert(Star, 'Alpha Centauri B', system=alpha_cen, spectral_type='K1V', mass_solar=0.91,
               temperature_k=5260, ra_deg=219.8961, dec_deg=-60.8375)
        upsert(Star, 'Proxima Centauri', system=alpha_cen, spectral_type='M5.5Ve', mass_solar=0.122,
               temperature_k=3042, ra_deg=217.4289, dec_deg=-62.6795,
               description='The nearest star to the Sun, at 4.24 light-years.')
        upsert(Planet, 'Proxima Centauri b', system=alpha_cen, mass_earth=1.07,
               orbital_period_days=11.19, is_exoplanet=True, ra_deg=217.4289, dec_deg=-62.6795,
               description='A rocky planet in the habitable zone of Proxima Centauri.')

        sirius = upsert(StarSystem, 'Sirius', galaxy=milky_way, distance_ly=8.6,
                        ra_deg=101.2872, dec_deg=-16.7161,
                        description='The brightest star in the night sky, with a white dwarf companion.')
        upsert(Star, 'Sirius A', system=sirius, spectral_type='A1V', mass_solar=2.06,
               temperature_k=9940, ra_deg=101.2872, dec_deg=-16.7161)
        upsert(Star, 'Sirius B', system=sirius, spectral_type='DA2', mass_solar=1.02,
               temperature_k=25000, ra_deg=101.2872, dec_deg=-16.7161,
               description='A white dwarf: the remnant core of a star, about the size of Earth.')

        betelgeuse = upsert(StarSystem, 'Betelgeuse', galaxy=milky_way, distance_ly=548,
                            ra_deg=88.7929, dec_deg=7.4071)
        upsert(Star, 'Betelgeuse', system=betelgeuse, spectral_type='M1Ia', mass_solar=18,
               temperature_k=3600, ra_deg=88.7929, dec_deg=7.4071,
               description='A red supergiant in Orion, expected to explode as a supernova within 100,000 years.')

        peg51 = upsert(StarSystem, '51 Pegasi', galaxy=milky_way, distance_ly=50.6,
                       ra_deg=344.3666, dec_deg=20.7688)
        upsert(Star, '51 Pegasi', system=peg51, spectral_type='G2IV', mass_solar=1.11,
               temperature_k=5768, ra_deg=344.3666, dec_deg=20.7688)
        upsert(Planet, '51 Pegasi b', system=peg51, mass_earth=150, radius_earth=None,
               orbital_period_days=4.23, is_exoplanet=True, ra_deg=344.3666, dec_deg=20.7688,
               description='The first exoplanet found around a Sun-like star (1995), a "hot Jupiter".')

        kepler452 = upsert(StarSystem, 'Kepler-452', galaxy=milky_way, distance_ly=1800,
                           ra_deg=296.0037, dec_deg=44.2776)
        upsert(Star, 'Kepler-452', system=kepler452, spectral_type='G2V', mass_solar=1.04,
               temperature_k=5757, ra_deg=296.0037, dec_deg=44.2776)
        upsert(Planet, 'Kepler-452b', system=kepler452, radius_earth=1.63,
               orbital_period_days=384.8, is_exoplanet=True, ra_deg=296.0037, dec_deg=44.2776,
               description='A super-Earth orbiting a Sun-like star in its habitable zone.')

        trappist = upsert(
            StarSystem, 'TRAPPIST-1', galaxy=milky_way, distance_ly=40.7,
            ra_deg=346.6223, dec_deg=-5.0414,
            description='An ultracool red dwarf with seven Earth-sized planets, three of them in the habitable zone.')
        upsert(Star, 'TRAPPIST-1', system=trappist, spectral_type='M8V', mass_solar=0.0898,
               temperature_k=2566, ra_deg=346.6223, dec_deg=-5.0414)
        for letter, mass, radius, period in [
            ('b', 1.374, 1.116, 1.511),
            ('c', 1.308, 1.097, 2.422),
            ('d', 0.388, 0.788, 4.049),
            ('e', 0.692, 0.920, 6.101),
            ('f', 1.039, 1.045, 9.207),
            ('g', 1.321, 1.129, 12.353),
            ('h', 0.326, 0.755, 18.773),
        ]:
            upsert(Planet, f'TRAPPIST-1{letter}', system=trappist, mass_earth=mass, radius_earth=radius,
                   orbital_period_days=period, is_exoplanet=True, ra_deg=346.6223, dec_deg=-5.0414)

        # ---------- Black holes ----------
        upsert(BlackHole, 'Sagittarius A*', galaxy=milky_way, bh_type='supermassive', mass_solar=4.3e6,
               ra_deg=266.4168, dec_deg=-29.0078,
               description='The supermassive black hole at the centre of the Milky Way, imaged by the Event Horizon Telescope in 2022.')
        upsert(BlackHole, 'Cygnus X-1', galaxy=milky_way, bh_type='stellar', mass_solar=21.2,
               ra_deg=299.5903, dec_deg=35.2016,
               description='The first object widely accepted to be a black hole (1971), feeding on a blue supergiant companion.')
        upsert(BlackHole, 'Gaia BH1', galaxy=milky_way, bh_type='stellar', mass_solar=9.62,
               ra_deg=262.1712, dec_deg=-0.5811,
               description='The nearest known black hole to Earth, about 1,560 light-years away (found in 2022).')
        upsert(BlackHole, 'M31*', galaxy=andromeda, bh_type='supermassive', mass_solar=1.4e8,
               ra_deg=10.6847, dec_deg=41.2690,
               description='The supermassive black hole at the centre of the Andromeda Galaxy.')
        upsert(BlackHole, 'M87*', galaxy=m87, bh_type='supermassive', mass_solar=6.5e9,
               ra_deg=187.7059, dec_deg=12.3911,
               description='The first black hole ever photographed (Event Horizon Telescope, 2019).')
        upsert(BlackHole, 'Centaurus A*', galaxy=centaurus_a, bh_type='supermassive', mass_solar=5.5e7,
               ra_deg=201.3651, dec_deg=-43.0191)
        upsert(BlackHole, '3C 273', galaxy=host_3c273, bh_type='quasar', mass_solar=8.86e8,
               luminosity_solar=4e12, redshift=0.158, ra_deg=187.2779, dec_deg=2.0524,
               description='The first quasar ever identified (1963) and the brightest in our sky.')
        upsert(BlackHole, 'TON 618', galaxy=host_ton618, bh_type='quasar', mass_solar=4.07e10,
               luminosity_solar=4e14, redshift=2.219, ra_deg=187.1038, dec_deg=31.4772,
               description='A hyperluminous quasar powered by one of the most massive black holes known.')

        counts = ', '.join(f'{model.objects.count()} {model._meta.verbose_name_plural}'
                           for model in [Galaxy, StarSystem, Star, Planet, Satellite, BlackHole])
        self.stdout.write(self.style.SUCCESS(f'Done. The database now has {counts}.'))
