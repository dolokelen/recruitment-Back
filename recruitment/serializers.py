from datetime import date
from rest_framework import serializers

from core.models import User
from core.serializers import ReadUserSerializer
from . import models


class ApplicationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicationDate
        fields = ['id', 'open_date', 'close_date', 'is_current']


class ApplicantDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicantDocument
        fields = ['qualification', 'graduation_year', 'major', 'manor', 'institution', 'country', 'county',
                  'cgpa', 'degree', 'application_letter', 'community_letter', 'reference_letter', 'resume', 'police_clearance']

    def create(self, validated_data):
        user_id = self.context['user_id']
        applicant = models.Applicant.objects.get(user_id=user_id)
        instance = models.ApplicantDocument.objects.create(
            applicant=applicant, **validated_data)

        return instance


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


class ReadApplicantSerializer(serializers.ModelSerializer):
    user = ReadUserSerializer()
    document = ApplicantDocumentSerializer()
    birth_date = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = models.Applicant
        fields = ['user', 'document', 'age', 'birth_date', 'gender', 'religion', 'county', 'image',
                  'id_number', 'status', 'rejection_reason']

    def get_birth_date(self, applicant):
        return applicant.birth_date.strftime('%B %d, %Y')

    def get_age(self, applicant):
        today = date.today()
        b_date = applicant.birth_date

        age = today.year - b_date.year - \
            ((today.month, today.day) < (b_date.month, b_date.day))

        return age
