from datetime import date
from django.db import transaction
from rest_framework import serializers

from core.serializers import ReadUserSerializer, UserCreateSerializer
from . import models


class ApplicationDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApplicationDate
        fields = ['id', 'open_date', 'close_date', 'is_current']

    def create(self, validated_data):
        instance = models.ApplicationDate.objects.create(**validated_data)
        application_stages = [
            {'name': 'Publicity', 'order': 1, 'is_current': True},
            {'name': 'Credential varification', 'order': 2},
            {'name': 'Writen exams', 'order': 3},
            {'name': 'Interview', 'order': 4},
            {'name': 'Job readiness orientation', 'order': 5},
            {'name': 'Placement', 'order': 6},
        ]

        for stage in application_stages:
            models.ApplicationStage.objects.create(**stage)

        return instance


class ReadApplicationDateSerializer(serializers.ModelSerializer):
    open_date = serializers.SerializerMethodField()
    close_date = serializers.SerializerMethodField()

    class Meta:
        model = models.ApplicationDate
        fields = ['id', 'open_date', 'close_date', 'is_current']

    def get_open_date(self, obj):
        return obj.open_date.strftime('%B %d, %Y')

    def get_close_date(self, obj):
        return obj.close_date.strftime('%B %d, %Y')


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

    def create(self, validated_data):
        instance = models.Applicant.objects.create(**validated_data)
        initial_stage = models.ApplicationStage.objects.get(is_current=True)
        initial_stage.applicants.add(instance.user.id)
        return instance


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


class EmployeeSerializer(serializers.ModelSerializer):
    """
    County represents the birth county of the employee
    """
    user = UserCreateSerializer()

    @transaction.atomic()
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserCreateSerializer(data=user_data)

        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.create(user_serializer.validated_data)
            instance = models.Employee.objects.create(
                user=user, **validated_data)

            return instance

    class Meta:
        model = models.Employee
        fields = ['user', 'birth_date', 'gender', 'religion', 'image',
                  'qualification', 'employment', 'position', 'supervisor', 'salary']


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeeDocument
        fields = ['id', 'employee', 'qualification', 'graduation_year', 'major', 'manor', 'institution', 'country', 'county',
                  'cgpa', 'degree', 'application_letter', 'community_letter', 'reference_letter', 'resume']


class EmployeeAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeeAddress
        fields = ['employee', 'country', 'county',
                  'district', 'community', 'house_address']


class EmployeeContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EmployeeContact
        fields = ['id', 'employee', 'phone']


class ReadEmployeeSerializer(serializers.ModelSerializer):
    user = ReadUserSerializer()
    documents = EmployeeDocumentSerializer(many=True)
    contacts = EmployeeContactSerializer(many=True)
    address = EmployeeAddressSerializer()
    birth_date = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = models.Employee
        fields = ['user', 'documents', 'address', 'contacts', 'age', 'birth_date', 'gender', 'religion', 'image',
                  'county', 'qualification', 'employment', 'position', 'supervisor', 'salary']

    def get_birth_date(self, emp):
        return emp.birth_date.strftime('%B %d, %Y')

    def get_age(self, emp):
        today = date.today()
        b_date = emp.birth_date

        age = today.year - b_date.year - \
            ((today.month, today.day) < (b_date.month, b_date.day))

        return age


class EmployeeSupervisorSerializer(serializers.ModelSerializer):
    """ 
    Return all supervisors NOT supervisees. 
    I'm not using ReadUserSerializer because it will add additional {}
    """
    id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Employee
        fields = ['id', 'full_name']

    def get_id(self, emp):
        return emp.user.id

    def get_full_name(self, emp):
        return f'{emp.user.first_name} {emp.user.last_name}'


class ReadQualifyApplicantSerializr(serializers.ModelSerializer):
    """Don't show any attr that can identify an applicant for transparency purpose"""
    user = ReadUserSerializer()
    document = ApplicantDocumentSerializer()
    stage_name = serializers.SerializerMethodField()
    stage_id = serializers.SerializerMethodField()

    class Meta:
        model = models.Applicant
        fields = ['user', 'document', 'id_number', 'status', 'stage_name', 'stage_id']

    def get_stage_name(self, applicant):
        stage_name = applicant.stages.filter(is_current=True)[0].name
        return stage_name if stage_name else ""
    
    def get_stage_id(self, applicant):
        """ Use when posting applicant screening data"""
        stage_id = applicant.stages.filter(is_current=True)[0].id
        return stage_id if stage_id else 0


class ApplicantScreeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Screening
        fields = ['id', 'status', 'rejection_reason',
                  'applicant', 'stage', 'process_by']
