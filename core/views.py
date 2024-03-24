from django.contrib.auth.models import Group, Permission
from rest_framework.viewsets import ModelViewSet

from . import serializers


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.prefetch_related('permissions').all()
    serializer_class = serializers.GroupSerializer


class PermissionViewSet(ModelViewSet):
    http_method_names = ['get', 'post']
    excluded_ids = [1, 2, 3, 4, 13, 14, 15, 16, 17, 18, 19, 20]
    queryset = Permission.objects.exclude(id__in=excluded_ids)
    serializer_class = serializers.PermissionSerializer
