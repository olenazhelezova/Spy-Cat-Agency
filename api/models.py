from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import BooleanField


class Cat(models.Model):
    name = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField()
    breed = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[
                                 MinValueValidator(Decimal('0.00'))])

    @property
    def current_mission(self):
        return self.missions.filter(is_complete=False).first()

    @property
    @extend_schema_field(BooleanField)
    def is_available(self):
        return self.current_mission is None

    def __str__(self):
        return f"ID {self.pk}: {self.name} ({self.breed}, {self.years_of_experience} yrs, ${self.salary})"


class Mission(models.Model):
    cat = models.ForeignKey(
        Cat, on_delete=models.SET_NULL, null=True, blank=True, related_name='missions'
    )
    is_complete = models.BooleanField(default=False)


class Target(models.Model):
    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name='targets')
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    notes = models.TextField(default="")
    is_complete = models.BooleanField(default=False)
