from django import forms
from .models import Galaxy


class GalaxyForm(forms.ModelForm):
    class Meta:
        model = Galaxy
        fields = ['name', 'galaxy_type', 'distance_ly', 'description']