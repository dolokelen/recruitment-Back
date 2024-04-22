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
        fields = ['applicant', 'qualification', 'graduation_year', 'major', 'manor', 'institution', 'country', 'county',
                  'ccgpa', 'degree', 'application_letter', 'community_letter', 'reference_letter', 'resume', 'police_clearance']


class ApplicantAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicantAddress
        fields = ['applicant', 'country', 'county_of_birth',
                  'district', 'community', 'house_address']


class ApplicantContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicantContact
        fields = ['id', 'phone']


class ApplicantSerializer(serializers.ModelSerializer):
    app_document = ApplicantDocumentSerializer()
    app_address = ApplicantAddressSerializer()
    app_contact = ApplicantContactSerializer(many=True)

    @transaction.atomic()
    def create(self, validated_data):
        document_data = validated_data.pop('app_document')
        address_data = validated_data.pop('app_address')
        contact_data = validated_data.pop('app_contact')
        
        user = User.objects.get(id=self.context['user_id'])
        applicant = models.Applicant.objects.create(user=user, **validated_data)
        
        document_serializer = ApplicantDocumentSerializer(data=document_data)
        if document_serializer.is_valid(raise_exception=True):
            document_serializer.save(applicant=applicant)

        address_serializer = ApplicantAddressSerializer(data=address_data)
        if address_serializer.is_valid(raise_exception=True):
            address_serializer.save(applicant=applicant)

        for contact in contact_data:
            contact_serializer = ApplicantContactSerializer(data=contact)
            if contact_serializer.is_valid(raise_exception=True):
                contact_serializer.save(applicant=applicant)

        return applicant

    class Meta:
        model = models.Applicant
        fields = ['app_document', 'app_address', 'app_contact', 'birth_date', 'gender',
                  'religion', 'image', 'id_number', 'status', 'rejection_reason']
