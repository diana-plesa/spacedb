from django.shortcuts import render, get_object_or_404, redirect
from .models import Galaxy
from .forms import GalaxyForm


def galaxy_list(request):
    galaxies = Galaxy.objects.all().order_by('name')
    return render(request, 'catalog/galaxy_list.html', {'galaxies': galaxies})


def galaxy_detail(request, pk):
    galaxy = get_object_or_404(Galaxy, pk=pk)
    return render(request, 'catalog/galaxy_detail.html', {'galaxy': galaxy})


def galaxy_create(request):
    form = GalaxyForm(request.POST or None)
    if form.is_valid():
        galaxy = form.save()
        return redirect('galaxy_detail', pk=galaxy.pk)
    return render(request, 'catalog/galaxy_form.html', {'form': form, 'title': 'Add galaxy'})


def galaxy_update(request, pk):
    galaxy = get_object_or_404(Galaxy, pk=pk)
    form = GalaxyForm(request.POST or None, instance=galaxy)
    if form.is_valid():
        form.save()
        return redirect('galaxy_detail', pk=galaxy.pk)
    return render(request, 'catalog/galaxy_form.html', {'form': form, 'title': 'Edit galaxy'})


def galaxy_delete(request, pk):
    galaxy = get_object_or_404(Galaxy, pk=pk)
    if request.method == 'POST':
        galaxy.delete()
        return redirect('galaxy_list')
    return render(request, 'catalog/galaxy_confirm_delete.html', {'galaxy': galaxy})