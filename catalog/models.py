import re

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse

# Finds the file name in a link to a Wikimedia Commons / Wikipedia file *page*, e.g.
#   https://commons.wikimedia.org/wiki/File:Moon.jpg
#   https://en.wikipedia.org/wiki/Moon#/media/File:Moon.jpg
FILE_PAGE_PATTERN = re.compile(r'^https?://[^/]*(wikipedia|wikimedia)\.org/.*File:([^?#]+)')


class CelestialObject(models.Model):
    """Fields shared by every object in the catalog. Not a table by itself."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    ra_deg = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(360)],
        help_text="Right ascension in degrees (0 to 360)",
    )
    dec_deg = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Declination in degrees (-90 to 90)",
    )
    image_url = models.URLField(
        max_length=500, blank=True, default='',
        help_text="Link to a picture, e.g. from Wikimedia Commons",
    )
    image_source = models.URLField(
        max_length=500, blank=True, default='',
        help_text="Page that credits the picture's author and licence",
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        # Django calls clean() while validating forms (ours and the admin's), before saving.
        # People usually paste the picture's web page rather than the picture itself, and a
        # web page can't be shown in an <img>. Turn it into a direct link to the picture,
        # and use the file's page (which names the author and licence) as the credit.
        match = FILE_PAGE_PATTERN.match(self.image_url)
        if match:
            file_name = match.group(2)
            self.image_url = f'https://commons.wikimedia.org/wiki/Special:FilePath/{file_name}?width=960'
            self.image_source = f'https://commons.wikimedia.org/wiki/File:{file_name}'

    def get_absolute_url(self):
        # e.g. 'galaxy_detail' or 'starsystem_detail', matching the names in urls.py
        return reverse(f'{self._meta.model_name}_detail', args=[self.pk])


class Galaxy(CelestialObject):
    TYPE_CHOICES = [
        ('spiral', 'Spiral'),
        ('elliptical', 'Elliptical'),
        ('irregular', 'Irregular'),
        ('lenticular', 'Lenticular'),
    ]

    galaxy_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    distance_ly = models.FloatField(help_text="Distance from Earth in light-years")

    class Meta(CelestialObject.Meta):
        verbose_name_plural = 'galaxies'


class StarSystem(CelestialObject):
    galaxy = models.ForeignKey(Galaxy, on_delete=models.CASCADE, related_name='star_systems')
    distance_ly = models.FloatField(help_text="Distance from Earth in light-years")


class Star(CelestialObject):
    system = models.ForeignKey(StarSystem, on_delete=models.CASCADE, related_name='stars')
    spectral_type = models.CharField(max_length=10, blank=True, help_text="e.g. G2V")
    mass_solar = models.FloatField(null=True, blank=True, help_text="Mass in solar masses")
    temperature_k = models.FloatField(null=True, blank=True, help_text="Surface temperature in kelvin")


class Planet(CelestialObject):
    system = models.ForeignKey(StarSystem, on_delete=models.CASCADE, related_name='planets')
    mass_earth = models.FloatField(null=True, blank=True, help_text="Mass in Earth masses")
    radius_earth = models.FloatField(null=True, blank=True, help_text="Radius in Earth radii")
    orbital_period_days = models.FloatField(null=True, blank=True)
    is_exoplanet = models.BooleanField(default=False)


class Satellite(CelestialObject):
    KIND_CHOICES = [
        ('natural', 'Natural'),
        ('artificial', 'Artificial'),
    ]

    planet = models.ForeignKey(Planet, on_delete=models.CASCADE, related_name='satellites')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)


class BlackHole(CelestialObject):
    TYPE_CHOICES = [
        ('stellar', 'Stellar'),
        ('supermassive', 'Supermassive'),
        ('quasar', 'Quasar'),
    ]

    galaxy = models.ForeignKey(Galaxy, on_delete=models.CASCADE, related_name='black_holes')
    bh_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    mass_solar = models.FloatField(null=True, blank=True, help_text="Mass in solar masses")
    luminosity_solar = models.FloatField(null=True, blank=True, help_text="Quasars only: luminosity in solar luminosities")
    redshift = models.FloatField(null=True, blank=True, help_text="Quasars only: redshift (z)")

    def clean(self):
        super().clean()  # keep the picture-link fix from CelestialObject
        if self.bh_type == 'quasar':
            if self.redshift is None:
                raise ValidationError({'redshift': 'A quasar needs a redshift.'})
        else:
            # Only quasars have these values; drop anything left over, e.g. after changing the type
            self.luminosity_solar = None
            self.redshift = None
