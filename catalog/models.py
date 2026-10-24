from django.db import models


class Galaxy(models.Model):
    TYPE_CHOICES = [
        ('spiral', 'Spiral'),
        ('elliptical', 'Elliptical'),
        ('irregular', 'Irregular'),
        ('lenticular', 'Lenticular'),
    ]

    name = models.CharField(max_length=100, unique=True)
    galaxy_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    distance_ly = models.FloatField(help_text="Distance from Earth in light-years")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name