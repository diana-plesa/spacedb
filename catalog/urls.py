from django.urls import path
from . import views

# URL names follow the pattern '<model name>_<action>' (e.g. 'starsystem_detail'),
# which CelestialObject.get_absolute_url and the shared views rely on.
urlpatterns = [
    path('', views.home, name='home'),

    path('galaxies/', views.GalaxyList.as_view(), name='galaxy_list'),
    path('galaxies/new/', views.GalaxyCreate.as_view(), name='galaxy_create'),
    path('galaxies/<int:pk>/', views.GalaxyDetail.as_view(), name='galaxy_detail'),
    path('galaxies/<int:pk>/edit/', views.GalaxyUpdate.as_view(), name='galaxy_update'),
    path('galaxies/<int:pk>/delete/', views.GalaxyDelete.as_view(), name='galaxy_delete'),

    path('star-systems/', views.StarSystemList.as_view(), name='starsystem_list'),
    path('star-systems/new/', views.StarSystemCreate.as_view(), name='starsystem_create'),
    path('star-systems/<int:pk>/', views.StarSystemDetail.as_view(), name='starsystem_detail'),
    path('star-systems/<int:pk>/edit/', views.StarSystemUpdate.as_view(), name='starsystem_update'),
    path('star-systems/<int:pk>/delete/', views.StarSystemDelete.as_view(), name='starsystem_delete'),

    path('stars/', views.StarList.as_view(), name='star_list'),
    path('stars/new/', views.StarCreate.as_view(), name='star_create'),
    path('stars/<int:pk>/', views.StarDetail.as_view(), name='star_detail'),
    path('stars/<int:pk>/edit/', views.StarUpdate.as_view(), name='star_update'),
    path('stars/<int:pk>/delete/', views.StarDelete.as_view(), name='star_delete'),

    path('planets/', views.PlanetList.as_view(), name='planet_list'),
    path('planets/new/', views.PlanetCreate.as_view(), name='planet_create'),
    path('planets/<int:pk>/', views.PlanetDetail.as_view(), name='planet_detail'),
    path('planets/<int:pk>/edit/', views.PlanetUpdate.as_view(), name='planet_update'),
    path('planets/<int:pk>/delete/', views.PlanetDelete.as_view(), name='planet_delete'),

    path('satellites/', views.SatelliteList.as_view(), name='satellite_list'),
    path('satellites/new/', views.SatelliteCreate.as_view(), name='satellite_create'),
    path('satellites/<int:pk>/', views.SatelliteDetail.as_view(), name='satellite_detail'),
    path('satellites/<int:pk>/edit/', views.SatelliteUpdate.as_view(), name='satellite_update'),
    path('satellites/<int:pk>/delete/', views.SatelliteDelete.as_view(), name='satellite_delete'),

    path('black-holes/', views.BlackHoleList.as_view(), name='blackhole_list'),
    path('black-holes/new/', views.BlackHoleCreate.as_view(), name='blackhole_create'),
    path('black-holes/<int:pk>/', views.BlackHoleDetail.as_view(), name='blackhole_detail'),
    path('black-holes/<int:pk>/edit/', views.BlackHoleUpdate.as_view(), name='blackhole_update'),
    path('black-holes/<int:pk>/delete/', views.BlackHoleDelete.as_view(), name='blackhole_delete'),
]
