import pytest
from django.contrib.auth.models import Permission, Group
from rest_framework import status

from core.models import User
from conftest import JWT, USER_TOKEN, USERS_ENDPOINT, user_payload

GROUPS_ENDPOINT = '/core/groups/'
PERMISSIONS_ENDPOINT = '/core/permissions/'


@pytest.mark.django_db
class TestPermission:
    def test_if_permissions_can_be_added_to_group(self, post, api_client, get, get_all):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        instance = Group.objects.get(id=response.data['id'])
        permissions_res = get_all(PERMISSIONS_ENDPOINT)
        permissions = permissions_res.json()  # b/c the response is a byte

        for permission in permissions:
            instance.permissions.add(permission['id'])

        removed_permissions = Permission.objects.filter(
            name__in=['Can view group', 'Can add group']).values_list('id', flat=True)

        instance.permissions.remove(*removed_permissions)
        updated_group = get(GROUPS_ENDPOINT, response.data['id'])

        assert len(updated_group.data['permissions']) < len(permissions)

    def test_if_a_permission_can_be_added_to_group(self, post, api_client, get, get_all):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        instance = Group.objects.get(id=response.data['id'])
        permissions_res = get_all(PERMISSIONS_ENDPOINT)
        permissions = permissions_res.json()  # b/c the response is a byte
        instance.permissions.add(permissions[0]['id'])
        updated_group = get(GROUPS_ENDPOINT, response.data['id'])

        assert len(updated_group.data['permissions']) == 1

    def test_if_a_permission_can_be_removed_from_group(self, post, api_client, get, get_all):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        instance = Group.objects.get(id=response.data['id'])
        permissions_res = get_all(PERMISSIONS_ENDPOINT)
        permissions = permissions_res.json()  # b/c the response is a byte

        instance.permissions.add(permissions[0]['id'])
        instance.permissions.remove(permissions[0]['id'])
        updated_group = get(GROUPS_ENDPOINT, response.data['id'])

        assert len(updated_group.data['permissions']) == 0

    def test_if_permissions_can_be_remove_from_group_return_200(self, post, api_client, get, get_all):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        instance = Group.objects.get(id=response.data['id'])
        permissions_res = get_all(PERMISSIONS_ENDPOINT)
        permissions = permissions_res.json()  # b/c the response is a byte

        for permission in permissions:
            instance.permissions.add(permission['id'])

        queryset = Permission.objects.filter(
            id__in=[5, 7]).values_list('id', flat=True)
        instance.permissions.remove(*queryset)
        updated_group = get(GROUPS_ENDPOINT, response.data['id'])

        assert len(updated_group.data['permissions']) < len(permissions)

    def test_if_authenticated_user_can_retrieve_permission_return_200(self, post, api_client, get_all):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = get_all(PERMISSIONS_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK

    def test_if_anonymous_user_cannot_retrieve_permission_return_401(self, post, get_all):
        post(USERS_ENDPOINT, user_payload())
        response = get_all(PERMISSIONS_ENDPOINT)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_can_inherit_its_group_permissions(self, post, api_client, get_all):
        response_user = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response_group = post(GROUPS_ENDPOINT, {'name': 'a'})
        response_permissions = get_all(PERMISSIONS_ENDPOINT)
        permissions = response_permissions.json()
        group_instance = Group.objects.get(id=response_group.data['id'])

        for permission in permissions:
            group_instance.permissions.add(permission['id'])

        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=[response_group.data['id']]).values_list('id', flat=True)
        user_instance.groups.add(*queryset)

        assert len(user_instance.groups.first(
        ).permissions.all()) == len(permissions)

    def test_if_user_can_be_remove_its_group_permissions(self, post, api_client, get_all):
        response_user = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response_group = post(GROUPS_ENDPOINT, {'name': 'a'})
        response_permissions = get_all(PERMISSIONS_ENDPOINT)
        permissions = response_permissions.json()
        group_instance = Group.objects.get(id=response_group.data['id'])

        for permission in permissions:
            group_instance.permissions.add(permission['id'])

        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=[response_group.data['id']]).values_list('id', flat=True)
        user_instance.groups.add(*queryset)

        assert len(user_instance.groups.first(
        ).permissions.all()) == len(permissions)
