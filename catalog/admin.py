from django.contrib import admin
from .models import Galaxy, StarSystem, Star, Planet, Satellite, BlackHole


@admin.register(Galaxy)
class GalaxyAdmin(admin.ModelAdmin):
    list_display = ('name', 'galaxy_type', 'distance_ly')
    search_fields = ('name',)
    list_filter = ('galaxy_type',)


# Inlines let you edit a system's stars and planets on the system's own admin page.
class StarInline(admin.TabularInline):
    model = Star
    extra = 0
    fields = ('name', 'spectral_type', 'mass_solar', 'temperature_k')


class PlanetInline(admin.TabularInline):
    model = Planet
    extra = 0
    fields = ('name', 'mass_earth', 'radius_earth', 'orbital_period_days', 'is_exoplanet')


@admin.register(StarSystem)
class StarSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'galaxy', 'distance_ly')
    search_fields = ('name',)
    list_filter = ('galaxy',)
    inlines = [StarInline, PlanetInline]


@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'spectral_type', 'mass_solar', 'temperature_k')
    search_fields = ('name', 'spectral_type')


@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'mass_earth', 'radius_earth', 'is_exoplanet')
    search_fields = ('name',)
    list_filter = ('is_exoplanet',)


@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    list_display = ('name', 'planet', 'kind')
    search_fields = ('name',)
    list_filter = ('kind',)


@admin.register(BlackHole)
class BlackHoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'galaxy', 'bh_type', 'mass_solar', 'redshift')
    search_fields = ('name',)
    list_filter = ('bh_type',)
