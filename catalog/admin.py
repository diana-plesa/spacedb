from django.contrib import admin
from .models import Galaxy


@admin.register(Galaxy)
class GalaxyAdmin(admin.ModelAdmin):
    list_display = ('name', 'galaxy_type', 'distance_ly')
    search_fields = ('name',)
    list_filter = ('galaxy_type',)