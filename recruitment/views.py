import os
from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from core import permissions
from . import models
from . import serializers


class Permission(ModelViewSet):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.ReadModelPermission()]
        if self.request.method == 'POST':
            return [permissions.CreateModelPermission()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.UpdateModelPermission()]
        if self.request.method == 'DELETE':
            return [permissions.DeleteModelPermission()]
        return super().get_permissions()


class ApplicationDateViewSet(Permission):
    queryset = models.ApplicationDate.objects.all()
    serializer_class = serializers.ApplicationDateSerializer


class ApplicantViewSet(ModelViewSet):  # You must apply permissions
    """
    Only applicant should post, if someone wants to 
    proxy they MUST use the applicant credentials to login.
    """
    queryset = models.Applicant.objects.select_related(
        'user', 'document', 'address').prefetch_related('contacts').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadApplicantSerializer
        return serializers.ApplicantSerializer

    def create(self, request, *args, **kwargs):
        """
        I'm using FormData to post because of the image(binary) and 
        each field is placed in a list
        """
        data = request.data.copy()
        applicant_data = {
            'user': data.pop('user')[0],
            'birth_date': data.pop('birth_date')[0],
            'gender': data.pop('gender')[0],
            'religion': data.pop('religion')[0],
            'county': data.pop('county')[0],
            'image': data.pop('image')[0],
        }

        serializer = self.get_serializer(data=applicant_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """ See validators.py for MAX_SIZE. Deleting the old image and saving the new one"""
        instance = self.get_object()
        new_image = request.data.get('image', None)

        if new_image:
            img_name = new_image.name
            _, extension = os.path.splitext(img_name)
            MAX_SIZE = 1024 * 300
            ALLOWED_EXTENSIONS = ['.jpg', '.png', '.jpeg', '.gif', '.webp']

            if new_image.size <= MAX_SIZE and instance.image and extension.lower() in ALLOWED_EXTENSIONS:
                old_image_path = os.path.join(
                    settings.MEDIA_ROOT, str(instance.image))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

        return super().update(request, *args, **kwargs)


class ApplicantDocumentViewSet(ModelViewSet):
    """
    If I get user_id from self.request.user.id and pass it to the 
    serializer using the context obj and override the create method,
    the Test for this view will fail because only the database Pytest
    does not commit during the test. When Pytest runs this view and 
    the value for self.request.user.id will not be available. 

    However, this will work with models that have DIRECT OneToOne relationship 
    to the User model. But for consistancy I won't use it at all.
    """
    queryset = models.ApplicantDocument.objects.select_related(
        'applicant').all()
    serializer_class = serializers.ApplicantDocumentSerializer

    def create(self, request, *args, **kwargs):
        """
        I'm using FormData to post because of the files(binary) and 
        each field is placed in a list

        See this class for generic comment
        """
        data = request.data.copy()
        document_data = {
            'applicant': data.pop('applicant')[0],
            'cgpa': data.pop('cgpa')[0],
            'qualification': data.pop('qualification')[0],
            'institution': data.pop('institution')[0],
            'major': data.pop('major')[0],
            'manor': data.pop('manor')[0],
            'country': data.pop('country')[0],
            'county': data.pop('county')[0],
            'graduation_year': data.pop('graduation_year')[0],
            'degree': data.pop('degree')[0],
            'application_letter': data.pop('application_letter')[0],
            'reference_letter': data.pop('reference_letter')[0],
            'community_letter': data.pop('community_letter')[0],
            'police_clearance': data.pop('police_clearance')[0],
            'resume': data.pop('resume')[0]
        }
        serializer = self.get_serializer(data=document_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApplicantAddressViewSet(ModelViewSet):
    """ 
    If I get user_id from self.request.user.id and pass it to the 
    serializer using the context obj and override the create method,
    the Test for this view will fail because only the database Pytest
    does not commit during the test. When Pytest runs this view and 
    the value for self.request.user.id will not be available. 

    However, this will work with models that have DIRECT OneToOne relationship 
    to the User model. But for consistancy I won't use it at all.
    """
    queryset = models.ApplicantAddress.objects.select_related(
        'applicant').all()
    serializer_class = serializers.ApplicantAddressSerializer


class ApplicantContactViewSet(ModelViewSet):
    queryset = models.ApplicantContact.objects.select_related('applicant')
    serializer_class = serializers.ApplicantContactSerializer


class EmployeeViewSet(Permission):
    queryset = models.Employee.objects.select_related(
        'user', 'address').prefetch_related('contacts', 'documents').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadEmployeeSerializer
        return serializers.EmployeeSerializer

    def create(self, request, *args, **kwargs):
        """
        I'm using FormData to post because of the image(binary) and 
        each field is placed in a list
        """
        data = request.data.copy()
        employee_data = {
            'user': data.pop('user')[0],
            'birth_date': data.pop('birth_date')[0],
            'gender': data.pop('gender')[0],
            'religion': data.pop('religion')[0],
            'image': data.pop('image')[0],
            'qualification': data.pop('qualification')[0],
            'employment': data.pop('employment')[0],
            'position': data.pop('position')[0],
            'salary': data.pop('salary')[0],
            'supervisor': data.pop('supervisor')[0],
        }

        serializer = self.get_serializer(data=employee_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """ See validators.py for MAX_SIZE. Deleting the old image and saving the new one"""
        instance = self.get_object()
        new_image = request.data.get('image', None)

        if new_image:
            img_name = new_image.name
            _, extension = os.path.splitext(img_name)
            MAX_SIZE = 1024 * 300
            ALLOWED_EXTENSIONS = ['.jpg', '.png', '.jpeg', '.gif', '.webp']

            if new_image.size <= MAX_SIZE and instance.image and extension.lower() in ALLOWED_EXTENSIONS:
                old_image_path = os.path.join(
                    settings.MEDIA_ROOT, str(instance.image))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

        return super().update(request, *args, **kwargs)


class EmployeeDocumentViewSet(ModelViewSet):
    queryset = models.EmployeeDocument.objects.select_related(
        'employee').all()
    serializer_class = serializers.EmployeeDocumentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        document_data = {
            'employee': data.pop('employee')[0],
            'qualification': data.pop('qualification')[0],
            'graduation_year': data.pop('graduation_year')[0],
            'major': data.pop('major')[0],
            'manor': data.pop('manor')[0],
            'institution': data.pop('institution')[0],
            'country': data.pop('country')[0],
            'county': data.pop('county')[0],
            'cgpa': data.pop('cgpa')[0],
            'degree': data.pop('degree')[0],
            'application_letter': data.pop('application_letter')[0],
            'community_letter': data.pop('community_letter')[0],
            'reference_letter': data.pop('reference_letter')[0],
            'resume': data.pop('resume')[0]
        }
        serializer = self.get_serializer(data=document_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmployeeAddressViewSet(ModelViewSet):
    """ 
    If I get user_id from self.request.user.id and pass it to the 
    serializer using the context obj and override the create method,
    the Test for this view will fail because only the database Pytest
    does not commit during the test. When Pytest runs this view and 
    the value for self.request.user.id will not be available. 

    However, this will work with models that have DIRECT OneToOne relationship 
    to the User model. But for consistancy I won't use it at all.
    """
    queryset = models.EmployeeAddress.objects.select_related(
        'employee').all()
    serializer_class = serializers.EmployeeAddressSerializer


class EmployeeContactViewSet(ModelViewSet):
    queryset = models.EmployeeContact.objects.select_related('employee')
    serializer_class = serializers.EmployeeContactSerializer