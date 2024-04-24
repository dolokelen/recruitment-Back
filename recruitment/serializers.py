from django.db import transaction
from rest_framework import serializers

from core.serializers import User
from . import models


class ApplicationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicationDate
        fields = ['id', 'open_date', 'close_date', 'is_current']


class ApplicantDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ApplicantDocument
        fields = ['id', 'applicant', 'qualification', 'graduation_year', 'major', 'manor', 'institution', 'country', 'county',
                  'cgpa', 'degree', 'application_letter', 'community_letter', 'reference_letter', 'resume', 'police_clearance']


class ApplicantAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicantAddress
        fields = ['applicant', 'country', 'county',
                  'district', 'community', 'house_address']


class ApplicantContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicantContact
        fields = ['id', 'phone']


class ApplicantSerializer(serializers.ModelSerializer):
    """
    County represents the birth county of the applicant
    """
    class Meta:
        model = models.Applicant
        fields = ['birth_date', 'gender', 'religion', 'county', 'image',
                  'id_number', 'status', 'rejection_reason']

    def create(self, validated_data):
        user = User.objects.get(id=self.context['user_id'])
        applicant = models.Applicant.objects.create(
            user=user, **validated_data)
        
        return applicant
       