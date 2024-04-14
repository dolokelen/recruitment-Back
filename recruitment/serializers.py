from rest_framework import serializers

from . import models


class ApplicationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicationDate
        fields = ['id', 'open_date', 'close_date', 'is_current']
