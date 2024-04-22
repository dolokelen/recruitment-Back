from rest_framework.viewsets import ModelViewSet

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


class ApplicantViewSet(ModelViewSet):
    """
    Only user who registered as applicant can access this view
    if an employee wants to proxy for an applicant the employee 
    must use the applicant username and password to login because
    the user_id will be associated with an Applicant automatically.
    """
    queryset = models.Applicant.objects.all()
    serializer_class = serializers.ApplicantSerializer

    def get_serializer_context(self):
        return {'user_id': self.kwargs['pk']}

    # def partial_update(self, request, *args, **kwargs):
    #     mutable_data = self.request.data.copy()
    #     user_id = self.kwargs['pk']
    #     print(mutable_data, user_id)
