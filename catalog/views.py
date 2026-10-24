from django.contrib.admin.utils import NestedObjects
from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Galaxy, StarSystem, Star, Planet, Satellite, BlackHole
from .forms import GalaxyForm, StarSystemForm, StarForm, PlanetForm, SatelliteForm, BlackHoleForm


def home(request):
    counts = [
        ('Galaxies', Galaxy.objects.count(), 'galaxy_list'),
        ('Star systems', StarSystem.objects.count(), 'starsystem_list'),
        ('Stars', Star.objects.count(), 'star_list'),
        ('Planets', Planet.objects.count(), 'planet_list'),
        ('Satellites', Satellite.objects.count(), 'satellite_list'),
        ('Black holes', BlackHole.objects.count(), 'blackhole_list'),
    ]
    return render(request, 'catalog/home.html', {'counts': counts})


# ---------- Shared behaviour for the create / edit / delete pages ----------

class CatalogPageMixin:
    """Gives the shared templates the model's display name and a link to its list page."""

    def get_list_url(self):
        return reverse(f'{self.model._meta.model_name}_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_name'] = self.model._meta.verbose_name
        context['model_name_plural'] = self.model._meta.verbose_name_plural
        context['list_url'] = self.get_list_url()
        return context


class ObjectFormMixin(CatalogPageMixin):
    template_name = 'catalog/object_form.html'

    def get_initial(self):
        # Lets links like /planets/new/?system=3 pre-fill the parent field.
        initial = super().get_initial()
        initial.update(self.request.GET.dict())
        return initial


class ObjectDeleteMixin(CatalogPageMixin):
    template_name = 'catalog/object_confirm_delete.html'

    def get_success_url(self):
        return self.get_list_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ask Django what CASCADE will delete along with this object (the admin does the same).
        collector = NestedObjects(using='default')
        collector.collect([self.object])
        context['cascade_counts'] = [
            (len(objs), model._meta.verbose_name if len(objs) == 1 else model._meta.verbose_name_plural)
            for model, objs in collector.model_objs.items()
            if model is not self.model
        ]
        return context


# ---------- Galaxies ----------

class GalaxyList(ListView):
    model = Galaxy
    context_object_name = 'galaxies'


class GalaxyDetail(DetailView):
    model = Galaxy


class GalaxyCreate(ObjectFormMixin, CreateView):
    model = Galaxy
    form_class = GalaxyForm


class GalaxyUpdate(ObjectFormMixin, UpdateView):
    model = Galaxy
    form_class = GalaxyForm


class GalaxyDelete(ObjectDeleteMixin, DeleteView):
    model = Galaxy


# ---------- Star systems ----------

class StarSystemList(ListView):
    context_object_name = 'systems'
    # annotate() adds the counts to each row in the same SQL query
    queryset = StarSystem.objects.select_related('galaxy').annotate(
        star_count=Count('stars', distinct=True),
        planet_count=Count('planets', distinct=True),
    )


class StarSystemDetail(DetailView):
    model = StarSystem


class StarSystemCreate(ObjectFormMixin, CreateView):
    model = StarSystem
    form_class = StarSystemForm


class StarSystemUpdate(ObjectFormMixin, UpdateView):
    model = StarSystem
    form_class = StarSystemForm


class StarSystemDelete(ObjectDeleteMixin, DeleteView):
    model = StarSystem


# ---------- Stars ----------

class StarList(ListView):
    context_object_name = 'stars'
    queryset = Star.objects.select_related('system')


class StarDetail(DetailView):
    model = Star


class StarCreate(ObjectFormMixin, CreateView):
    model = Star
    form_class = StarForm


class StarUpdate(ObjectFormMixin, UpdateView):
    model = Star
    form_class = StarForm


class StarDelete(ObjectDeleteMixin, DeleteView):
    model = Star


# ---------- Planets ----------

class PlanetList(ListView):
    context_object_name = 'planets'
    queryset = Planet.objects.select_related('system')


class PlanetDetail(DetailView):
    model = Planet


class PlanetCreate(ObjectFormMixin, CreateView):
    model = Planet
    form_class = PlanetForm


class PlanetUpdate(ObjectFormMixin, UpdateView):
    model = Planet
    form_class = PlanetForm


class PlanetDelete(ObjectDeleteMixin, DeleteView):
    model = Planet


# ---------- Satellites ----------

class SatelliteList(ListView):
    context_object_name = 'satellites'
    queryset = Satellite.objects.select_related('planet')


class SatelliteDetail(DetailView):
    model = Satellite


class SatelliteCreate(ObjectFormMixin, CreateView):
    model = Satellite
    form_class = SatelliteForm


class SatelliteUpdate(ObjectFormMixin, UpdateView):
    model = Satellite
    form_class = SatelliteForm


class SatelliteDelete(ObjectDeleteMixin, DeleteView):
    model = Satellite


# ---------- Black holes ----------

class BlackHoleList(ListView):
    context_object_name = 'black_holes'
    queryset = BlackHole.objects.select_related('galaxy')


class BlackHoleDetail(DetailView):
    model = BlackHole


class BlackHoleCreate(ObjectFormMixin, CreateView):
    model = BlackHole
    form_class = BlackHoleForm


class BlackHoleUpdate(ObjectFormMixin, UpdateView):
    model = BlackHole
    form_class = BlackHoleForm


class BlackHoleDelete(ObjectDeleteMixin, DeleteView):
    model = BlackHole
