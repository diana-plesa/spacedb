from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('galaxies/', views.galaxy_list, name='galaxy_list'),
    path('galaxies/new/', views.galaxy_create, name='galaxy_create'),
    path('galaxies/<int:pk>/', views.galaxy_detail, name='galaxy_detail'),
    path('galaxies/<int:pk>/edit/', views.galaxy_update, name='galaxy_update'),
    path('galaxies/<int:pk>/delete/', views.galaxy_delete, name='galaxy_delete'),
]