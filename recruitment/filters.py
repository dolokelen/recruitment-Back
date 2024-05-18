from django_filters.rest_framework import FilterSet
from . import models

class EmployeeFilter(FilterSet):
    """ Filtering by both fields and related models"""
    class Meta:
        model = models.Employee
        fields = {
            'supervisor': ['exact'],
            'user': ['exact'],
            'county': ['exact'],
        }
