from rest_framework import serializers

from . import models


class ApplicationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicationDate
        fields = ['id', 'open_year', 'open_month', 'open_date',
                  'close_year', 'close_month', 'close_date']
