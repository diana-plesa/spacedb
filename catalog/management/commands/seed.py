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


# Pictures from Wikipedia / Wikimedia Commons: object name -> (image URL, page with author and licence).
# Objects with the same name in different tables (e.g. the Betelgeuse system and star) share a picture.
IMAGES = {
    'Milky Way': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/ESO-VLT-Laser-phot-33a-07.jpg/960px-ESO-VLT-Laser-phot-33a-07.jpg',
        'https://commons.wikimedia.org/wiki/File:ESO-VLT-Laser-phot-33a-07.jpg'),
    'Andromeda': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/5/57/M31-Andromede-16-09-2023-Hamois.jpg/960px-M31-Andromede-16-09-2023-Hamois.jpg',
        'https://commons.wikimedia.org/wiki/File:M31-Andromede-16-09-2023-Hamois.jpg'),
    'Triangulum Galaxy': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/6/64/VST_snaps_a_very_detailed_view_of_the_Triangulum_Galaxy.jpg/960px-VST_snaps_a_very_detailed_view_of_the_Triangulum_Galaxy.jpg',
        'https://commons.wikimedia.org/wiki/File:VST_snaps_a_very_detailed_view_of_the_Triangulum_Galaxy.jpg'),
    'Large Magellanic Cloud': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3c/Eso1021d.jpg/960px-Eso1021d.jpg',
        'https://commons.wikimedia.org/wiki/File:Eso1021d.jpg'),
    'Small Magellanic Cloud': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7a/Small_Magellanic_Cloud_%28Digitized_Sky_Survey_2%29.jpg/960px-Small_Magellanic_Cloud_%28Digitized_Sky_Survey_2%29.jpg',
        'https://commons.wikimedia.org/wiki/File:Small_Magellanic_Cloud_%28Digitized_Sky_Survey_2%29.jpg'),
    'Whirlpool Galaxy': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/db/Messier51_sRGB.jpg/960px-Messier51_sRGB.jpg',
        'https://commons.wikimedia.org/wiki/File:Messier51_sRGB.jpg'),
    'Messier 87': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/07/Messier_87_Hubble_WikiSky.jpg/960px-Messier_87_Hubble_WikiSky.jpg',
        'https://commons.wikimedia.org/wiki/File:Messier_87_Hubble_WikiSky.jpg'),
    'Centaurus A': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d2/ESO_Centaurus_A_LABOCA.jpg/960px-ESO_Centaurus_A_LABOCA.jpg',
        'https://commons.wikimedia.org/wiki/File:ESO_Centaurus_A_LABOCA.jpg'),
    '3C 273 host galaxy': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7b/Best_image_of_bright_quasar_3C_273_%2810953173335%29.jpg/960px-Best_image_of_bright_quasar_3C_273_%2810953173335%29.jpg',
        'https://commons.wikimedia.org/wiki/File:Best_image_of_bright_quasar_3C_273_%2810953173335%29.jpg'),
    'TON 618 host galaxy': (
        'https://upload.wikimedia.org/wikipedia/commons/e/e1/TON_618_SDSS9_version_3.jpg',
        'https://commons.wikimedia.org/wiki/File:TON_618_SDSS9_version_3.jpg'),
    'Solar System': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/28/Solar_System_True_Color_EN.png/960px-Solar_System_True_Color_EN.png',
        'https://commons.wikimedia.org/wiki/File:Solar_System_True_Color_EN.png'),
    'Alpha Centauri': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/3/31/The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg/960px-The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg',
        'https://commons.wikimedia.org/wiki/File:The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg'),
    'Sirius': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c9/Sirius_A_and_B_artwork.jpg/960px-Sirius_A_and_B_artwork.jpg',
        'https://commons.wikimedia.org/wiki/File:Sirius_A_and_B_artwork.jpg'),
    'Betelgeuse': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/5/57/Betelgeuse_captured_by_ALMA.jpg/960px-Betelgeuse_captured_by_ALMA.jpg',
        'https://commons.wikimedia.org/wiki/File:Betelgeuse_captured_by_ALMA.jpg'),
    '51 Pegasi': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/dc/Wide-field_view_of_the_sky_around_the_star_51_Pegasi_%28eso1517c%29_%28cropped%29.jpg/960px-Wide-field_view_of_the_sky_around_the_star_51_Pegasi_%28eso1517c%29_%28cropped%29.jpg',
        'https://commons.wikimedia.org/wiki/File:Wide-field_view_of_the_sky_around_the_star_51_Pegasi_%28eso1517c%29_%28cropped%29.jpg'),
    'Kepler-452': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/23/Kepler-452b_System.jpg/960px-Kepler-452b_System.jpg',
        'https://commons.wikimedia.org/wiki/File:Kepler-452b_System.jpg'),
    'TRAPPIST-1': (
        'https://upload.wikimedia.org/wikipedia/commons/a/a5/TRAPPIST-1_SDSS_2009-09-28_square_crop.png',
        'https://commons.wikimedia.org/wiki/File:TRAPPIST-1_SDSS_2009-09-28_square_crop.png'),
    'Sun': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/8/83/The_Sun_in_white_light.jpg/960px-The_Sun_in_white_light.jpg',
        'https://commons.wikimedia.org/wiki/File:The_Sun_in_white_light.jpg'),
    'Alpha Centauri A': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/3/31/The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg/960px-The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg',
        'https://commons.wikimedia.org/wiki/File:The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg'),
    'Alpha Centauri B': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/3/31/The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg/960px-The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg',
        'https://commons.wikimedia.org/wiki/File:The_sky_around_Alpha_Centauri_and_Proxima_Centauri_%28eso1629i%29.jpg'),
    'Proxima Centauri': (
        'https://upload.wikimedia.org/wikipedia/commons/9/95/New_shot_of_Proxima_Centauri%2C_our_nearest_neighbour.jpg',
        'https://commons.wikimedia.org/wiki/File:New_shot_of_Proxima_Centauri%2C_our_nearest_neighbour.jpg'),
    'Sirius A': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c9/Sirius_A_and_B_artwork.jpg/960px-Sirius_A_and_B_artwork.jpg',
        'https://commons.wikimedia.org/wiki/File:Sirius_A_and_B_artwork.jpg'),
    'Sirius B': (
        'https://upload.wikimedia.org/wikipedia/commons/1/18/Sirius_A_and_B_Hubble_photo.editted.PNG',
        'https://commons.wikimedia.org/wiki/File:Sirius_A_and_B_Hubble_photo.editted.PNG'),
    'Mercury': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4a/Mercury_in_true_color.jpg/960px-Mercury_in_true_color.jpg',
        'https://commons.wikimedia.org/wiki/File:Mercury_in_true_color.jpg'),
    'Venus': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/08/Venus_from_Mariner_10.jpg/960px-Venus_from_Mariner_10.jpg',
        'https://commons.wikimedia.org/wiki/File:Venus_from_Mariner_10.jpg'),
    'Earth': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2d/Meteosat-12-fci-march-equinox-2025-noon.jpg/960px-Meteosat-12-fci-march-equinox-2025-noon.jpg',
        'https://commons.wikimedia.org/wiki/File:Meteosat-12-fci-march-equinox-2025-noon.jpg'),
    'Mars': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0c/Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png/960px-Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png',
        'https://commons.wikimedia.org/wiki/File:Mars_-_August_30_2021_-_Flickr_-_Kevin_M._Gill.png'),
    'Jupiter': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e2/Jupiter_OPAL_2024.png/960px-Jupiter_OPAL_2024.png',
        'https://commons.wikimedia.org/wiki/File:Jupiter_OPAL_2024.png'),
    'Saturn': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/43/Saturn_global_view_from_Cassini%2C_rings_open_Better_Colour.png/960px-Saturn_global_view_from_Cassini%2C_rings_open_Better_Colour.png',
        'https://commons.wikimedia.org/wiki/File:Saturn_global_view_from_Cassini%2C_rings_open_Better_Colour.png'),
    'Uranus': (
        'https://upload.wikimedia.org/wikipedia/commons/6/69/Uranus_Voyager2_color_calibrated.png',
        'https://commons.wikimedia.org/wiki/File:Uranus_Voyager2_color_calibrated.png'),
    'Neptune': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b9/Neptune_Voyager2_color_calibrated.png/960px-Neptune_Voyager2_color_calibrated.png',
        'https://commons.wikimedia.org/wiki/File:Neptune_Voyager2_color_calibrated.png'),
    'Proxima Centauri b': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/8/81/Artist%E2%80%99s_impression_of_Proxima_Centauri_b_shown_hypothetically_as_an_arid_rocky_super-earth.jpg/960px-Artist%E2%80%99s_impression_of_Proxima_Centauri_b_shown_hypothetically_as_an_arid_rocky_super-earth.jpg',
        'https://commons.wikimedia.org/wiki/File:Artist%E2%80%99s_impression_of_Proxima_Centauri_b_shown_hypothetically_as_an_arid_rocky_super-earth.jpg'),
    '51 Pegasi b': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f7/Artist_impression_of_the_exoplanet_51_Pegasi_b.jpg/960px-Artist_impression_of_the_exoplanet_51_Pegasi_b.jpg',
        'https://commons.wikimedia.org/wiki/File:Artist_impression_of_the_exoplanet_51_Pegasi_b.jpg'),
    'Kepler-452b': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/ed/Kepler-452b_artist_concept.jpg/960px-Kepler-452b_artist_concept.jpg',
        'https://commons.wikimedia.org/wiki/File:Kepler-452b_artist_concept.jpg'),
    'TRAPPIST-1b': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3b/TRAPPIST-1_b_comparison.png/960px-TRAPPIST-1_b_comparison.png',
        'https://commons.wikimedia.org/wiki/File:TRAPPIST-1_b_comparison.png'),
    'TRAPPIST-1c': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a0/Rocky_Exoplanet_TRAPPIST-1_c_%28Artist_Concept%29.jpg/960px-Rocky_Exoplanet_TRAPPIST-1_c_%28Artist_Concept%29.jpg',
        'https://commons.wikimedia.org/wiki/File:Rocky_Exoplanet_TRAPPIST-1_c_%28Artist_Concept%29.jpg'),
    'TRAPPIST-1d': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7d/Artist_impression_of_TRAPPIST-1_d.jpg/960px-Artist_impression_of_TRAPPIST-1_d.jpg',
        'https://commons.wikimedia.org/wiki/File:Artist_impression_of_TRAPPIST-1_d.jpg'),
    'TRAPPIST-1e': (
        'https://upload.wikimedia.org/wikipedia/commons/3/38/TRAPPIST-1e_artist_impression_2018.png',
        'https://commons.wikimedia.org/wiki/File:TRAPPIST-1e_artist_impression_2018.png'),
    'TRAPPIST-1f': (
        'https://upload.wikimedia.org/wikipedia/commons/8/84/TRAPPIST-1f_artist_impression_2018.png',
        'https://commons.wikimedia.org/wiki/File:TRAPPIST-1f_artist_impression_2018.png'),
    'TRAPPIST-1g': (
        'https://upload.wikimedia.org/wikipedia/commons/5/54/TRAPPIST-1g_artist_impression_2018.png',
        'https://commons.wikimedia.org/wiki/File:TRAPPIST-1g_artist_impression_2018.png'),
    'TRAPPIST-1h': (
        'https://upload.wikimedia.org/wikipedia/commons/0/03/TRAPPIST-1h_artist_impression_2018.png',
        'https://commons.wikimedia.org/wiki/File:TRAPPIST-1h_artist_impression_2018.png'),
    'Moon': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e1/FullMoon2010.jpg/960px-FullMoon2010.jpg',
        'https://commons.wikimedia.org/wiki/File:FullMoon2010.jpg'),
    'International Space Station': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/5/59/The_station_pictured_from_the_SpaceX_Crew_Dragon_5.jpg/960px-The_station_pictured_from_the_SpaceX_Crew_Dragon_5.jpg',
        'https://commons.wikimedia.org/wiki/File:The_station_pictured_from_the_SpaceX_Crew_Dragon_5.jpg'),
    'Hubble Space Telescope': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4a/Hubble_2009_close-up_2.jpg/960px-Hubble_2009_close-up_2.jpg',
        'https://commons.wikimedia.org/wiki/File:Hubble_2009_close-up_2.jpg'),
    'Phobos': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/5/5c/Phobos_colour_2008.jpg/960px-Phobos_colour_2008.jpg',
        'https://commons.wikimedia.org/wiki/File:Phobos_colour_2008.jpg'),
    'Deimos': (
        'https://upload.wikimedia.org/wikipedia/commons/8/86/NASA-Deimos-MarsMoon-20090221.jpg',
        'https://commons.wikimedia.org/wiki/File:NASA-Deimos-MarsMoon-20090221.jpg'),
    'Io': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/07/Io_highest_resolution_natural_color.png/960px-Io_highest_resolution_natural_color.png',
        'https://commons.wikimedia.org/wiki/File:Io_highest_resolution_natural_color.png'),
    'Europa': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b3/Europa_-_Perijove_45_%28cropped%29.png/960px-Europa_-_Perijove_45_%28cropped%29.png',
        'https://commons.wikimedia.org/wiki/File:Europa_-_Perijove_45_%28cropped%29.png'),
    'Ganymede': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/21/Ganymede_-_Perijove_34_Composite.png/960px-Ganymede_-_Perijove_34_Composite.png',
        'https://commons.wikimedia.org/wiki/File:Ganymede_-_Perijove_34_Composite.png'),
    'Callisto': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c6/Callisto_VGR2_C2060635_OGB.png/960px-Callisto_VGR2_C2060635_OGB.png',
        'https://commons.wikimedia.org/wiki/File:Callisto_VGR2_C2060635_OGB.png'),
    'Titan': (
        'https://upload.wikimedia.org/wikipedia/commons/f/fe/Titan_in_true_color_by_Kevin_M._Gill.jpg',
        'https://commons.wikimedia.org/wiki/File:Titan_in_true_color_by_Kevin_M._Gill.jpg'),
    'Enceladus': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/8/83/PIA17202_-_Approaching_Enceladus.jpg/960px-PIA17202_-_Approaching_Enceladus.jpg',
        'https://commons.wikimedia.org/wiki/File:PIA17202_-_Approaching_Enceladus.jpg'),
    'Triton': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/9/98/Triton-usgs23-with-frame.jpg/960px-Triton-usgs23-with-frame.jpg',
        'https://commons.wikimedia.org/wiki/File:Triton-usgs23-with-frame.jpg'),
    'Sagittarius A*': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/9/96/EHT_Saggitarius_A_black_hole.tif/lossy-page1-960px-EHT_Saggitarius_A_black_hole.tif.jpg',
        'https://commons.wikimedia.org/wiki/File:EHT_Saggitarius_A_black_hole.tif'),
    'Cygnus X-1': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/af/Cygnus_X-1.png/960px-Cygnus_X-1.png',
        'https://commons.wikimedia.org/wiki/File:Cygnus_X-1.png'),
    'Gaia BH1': (
        'https://upload.wikimedia.org/wikipedia/commons/d/d2/Gaia_BH1_PanSTARRS.jpg',
        'https://commons.wikimedia.org/wiki/File:Gaia_BH1_PanSTARRS.jpg'),
    'M31*': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/5/57/M31-Andromede-16-09-2023-Hamois.jpg/960px-M31-Andromede-16-09-2023-Hamois.jpg',
        'https://commons.wikimedia.org/wiki/File:M31-Andromede-16-09-2023-Hamois.jpg'),
    'M87*': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/4f/Black_hole_-_Messier_87_crop_max_res.jpg/960px-Black_hole_-_Messier_87_crop_max_res.jpg',
        'https://commons.wikimedia.org/wiki/File:Black_hole_-_Messier_87_crop_max_res.jpg'),
    'Centaurus A*': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d2/ESO_Centaurus_A_LABOCA.jpg/960px-ESO_Centaurus_A_LABOCA.jpg',
        'https://commons.wikimedia.org/wiki/File:ESO_Centaurus_A_LABOCA.jpg'),
    '3C 273': (
        'https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7b/Best_image_of_bright_quasar_3C_273_%2810953173335%29.jpg/960px-Best_image_of_bright_quasar_3C_273_%2810953173335%29.jpg',
        'https://commons.wikimedia.org/wiki/File:Best_image_of_bright_quasar_3C_273_%2810953173335%29.jpg'),
    'TON 618': (
        'https://upload.wikimedia.org/wikipedia/commons/e/e1/TON_618_SDSS9_version_3.jpg',
        'https://commons.wikimedia.org/wiki/File:TON_618_SDSS9_version_3.jpg'),
}


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

        # ---------- Pictures (only for objects that don't have one yet) ----------
        for model in [Galaxy, StarSystem, Star, Planet, Satellite, BlackHole]:
            for obj in model.objects.filter(name__in=IMAGES, image_url=''):
                obj.image_url, obj.image_source = IMAGES[obj.name]
                obj.save()

        counts = ', '.join(f'{model.objects.count()} {model._meta.verbose_name_plural}'
                           for model in [Galaxy, StarSystem, Star, Planet, Satellite, BlackHole])
        self.stdout.write(self.style.SUCCESS(f'Done. The database now has {counts}.'))
