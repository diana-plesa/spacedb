from django import forms
from .models import Galaxy, StarSystem, Star, Planet, Satellite, BlackHole


class GalaxyForm(forms.ModelForm):
    class Meta:
        model = Galaxy
        fields = ['name', 'galaxy_type', 'distance_ly', 'ra_deg', 'dec_deg', 'image_url', 'image_source', 'description']


class StarSystemForm(forms.ModelForm):
    class Meta:
        model = StarSystem
        fields = ['name', 'galaxy', 'distance_ly', 'ra_deg', 'dec_deg', 'image_url', 'image_source', 'description']


class StarForm(forms.ModelForm):
    class Meta:
        model = Star
        fields = ['name', 'system', 'spectral_type', 'mass_solar', 'temperature_k',
                  'ra_deg', 'dec_deg', 'image_url', 'image_source', 'description']


class PlanetForm(forms.ModelForm):
    class Meta:
        model = Planet
        fields = ['name', 'system', 'mass_earth', 'radius_earth', 'orbital_period_days',
                  'is_exoplanet', 'ra_deg', 'dec_deg', 'image_url', 'image_source', 'description']


class SatelliteForm(forms.ModelForm):
    class Meta:
        model = Satellite
        fields = ['name', 'planet', 'kind', 'ra_deg', 'dec_deg', 'image_url', 'image_source', 'description']


class BlackHoleForm(forms.ModelForm):
    class Meta:
        model = BlackHole
        fields = ['name', 'galaxy', 'bh_type', 'mass_solar', 'luminosity_solar', 'redshift',
                  'ra_deg', 'dec_deg', 'image_url', 'image_source', 'description']
    # The quasar rules live in BlackHole.clean() in models.py, so the admin follows them too.
