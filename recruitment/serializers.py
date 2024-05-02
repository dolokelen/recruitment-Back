from datetime import date
from rest_framework import serializers

from core.serializers import ReadUserSerializer
from . import models


class ApplicationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicationDate
        fields = ['id', 'open_date', 'close_date', 'is_current']


class ApplicantDocumentSerializer(serializers.ModelSerializer):
    """ The user_id is the same as applicant due to their OneToOne relationship"""
    class Meta:
        model = models.ApplicantDocument
        fields = ['applicant', 'qualification', 'graduation_year', 'major', 'manor', 'institution', 'country', 'county',
                  'cgpa', 'degree', 'application_letter', 'community_letter', 'reference_letter', 'resume', 'police_clearance']


class ApplicantAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicantAddress
        fields = ['applicant', 'country', 'county',
                  'district', 'community', 'house_address']


class ApplicantContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicantContact
        fields = ['id', 'applicant', 'phone']


class ApplicantSerializer(serializers.ModelSerializer):
    """
    County represents the birth county of the applicant
    """
    class Meta:
        model = models.Applicant
        fields = ['user', 'birth_date', 'gender', 'religion', 'county', 'image',
                  'id_number', 'status', 'rejection_reason']


class ReadApplicantSerializer(serializers.ModelSerializer):
    user = ReadUserSerializer()
    document = ApplicantDocumentSerializer()
    contacts = ApplicantContactSerializer(many=True)
    address = ApplicantAddressSerializer()
    birth_date = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = models.Applicant
        fields = ['user', 'document', 'address', 'contacts', 'age', 'birth_date', 'gender', 'religion', 'county', 'image',
                  'id_number', 'status', 'rejection_reason']

    def get_birth_date(self, applicant):
        return applicant.birth_date.strftime('%B %d, %Y')

    def get_age(self, applicant):
        today = date.today()
        b_date = applicant.birth_date

        age = today.year - b_date.year - \
            ((today.month, today.day) < (b_date.month, b_date.day))

        return age
