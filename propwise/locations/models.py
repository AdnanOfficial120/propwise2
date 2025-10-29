# locations/models.py

from django.db import models

class City(models.Model):
    """
    Model to store city names, e.g., 'Lahore', 'Karachi'.
    """
    name = models.CharField(max_length=100, unique=True)
    # We can add more fields later, like state/province.
    
    class Meta:
        verbose_name_plural = "Cities" # Fixes "Citys" in the admin panel

    def __str__(self):
        return self.name

class Area(models.Model):
    """
    Model to store specific areas/neighborhoods within a city.
    e.g., 'DHA Phase 6', 'Gulberg 3'
    """
    name = models.CharField(max_length=150)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="areas")
    
    # We will add these fields later for our "Neighborhood Insights" feature:
    # latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        # Ensures that one city cannot have two areas with the same name
        unique_together = ('name', 'city')
    
    def __str__(self):
        return f"{self.name}, {self.city.name}"