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


class ApplicantViewSet(ModelViewSet): #You must apply permissions
    """
    Only applicant should post, if someone wants to 
    proxy they MUST use the applicant credentials to login.
    """
    queryset = models.Applicant.objects.select_related('user').all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ReadApplicantSerializer
        return serializers.ApplicantSerializer

    def get_serializer_context(self):
        """
        The user who is posting the data user_id is use to associate
        applicant with user.
        """
        return {'user_id': self.request.user.id}

    def create(self, request, *args, **kwargs):
        """
        I'm using FormData to post because of the image(binary) and 
        each field is placed in a list
        """
        data = request.data.copy()
        applicant_data = {
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
