from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


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

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

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
