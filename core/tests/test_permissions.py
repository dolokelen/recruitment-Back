import pytest
from django.contrib.auth.models import Permission, Group
from rest_framework import status

from core.models import User


@pytest.fixture
def create_user(api_client):
    def do_create_user(user_payload):
        return api_client.post('/auth/users/', user_payload)
    return do_create_user


@pytest.fixture
def create_group(api_client):
    def do_create_group(payload):
        return api_client.post('/core/groups/', payload)
    return do_create_group


@pytest.fixture
def get_group(api_client):
    def do_get_group(id):
        return api_client.get(f'/core/groups/{id}/')
    return do_get_group


@pytest.fixture
def get_permissions(api_client):
    def do_get_permissions():
        return api_client.get('/core/permissions/')
    return do_get_permissions


token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExMzU1Mjc1LCJpYXQiOjE3MTExODI0NzUsImp0aSI6Ijk4ZmM5ZTBhYWIyNjQ3YzViM2Y2Y2UwZjY2ZWM2Yzc4IiwidXNlcl9pZCI6MX0.zKtwdAv7-6XdryhtKysYZAg3roin7uhRnyolepmrMNo'


@pytest.mark.django_db
class TestPermission:
    def user_payload(self, email='d@gmail.com', first_name='a', last_name='b',
                     password='Django123', confirm_password='Django123'):
        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'confirm_password': confirm_password
        }

    def test_if_permissions_can_be_added_to_group(self, create_user, api_client, create_group, get_group, get_permissions):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        instance = Group.objects.get(id=response.data['id'])
        permissions_res = get_permissions()
        permissions = permissions_res.json()  # b/c the response is a byte

        for permission in permissions:
            instance.permissions.add(permission['id'])

        removed_permissions = Permission.objects.filter(
            name__in=['Can view group', 'Can add group']).values_list('id', flat=True)

        instance.permissions.remove(*removed_permissions)
        updated_group = get_group(response.data['id'])

        assert len(updated_group.data['permissions']) < len(permissions)

    def test_if_a_permission_can_be_added_to_group(self, create_user, api_client, create_group, get_group, get_permissions):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        instance = Group.objects.get(id=response.data['id'])
        permissions_res = get_permissions()
        permissions = permissions_res.json()  # b/c the response is a byte
        instance.permissions.add(permissions[0]['id'])
        updated_group = get_group(response.data['id'])

        assert len(updated_group.data['permissions']) == 1

    def test_if_a_permission_can_be_removed_from_group(self, create_user, api_client, create_group, get_group, get_permissions):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        instance = Group.objects.get(id=response.data['id'])
        permissions_res = get_permissions()
        permissions = permissions_res.json()  # b/c the response is a byte

        instance.permissions.add(permissions[0]['id'])
        instance.permissions.remove(permissions[0]['id'])
        updated_group = get_group(response.data['id'])

        assert len(updated_group.data['permissions']) == 0

    def test_if_permissions_can_be_remove_from_group_return_200(self, create_user, api_client, create_group, get_group, get_permissions):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        instance = Group.objects.get(id=response.data['id'])
        permissions_res = get_permissions()
        permissions = permissions_res.json()  # b/c the response is a byte

        for permission in permissions:
            instance.permissions.add(permission['id'])

        queryset = Permission.objects.filter(
            id__in=[5, 7]).values_list('id', flat=True)
        instance.permissions.remove(*queryset)
        updated_group = get_group(response.data['id'])

        assert len(updated_group.data['permissions']) < len(permissions)

    def test_if_authenticated_user_can_retrieve_permission_return_200(self, create_user, api_client, get_permissions):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = get_permissions()

        assert response.status_code == status.HTTP_200_OK

    def test_if_anonymous_user_cannot_retrieve_permission_return_401(self, create_user, api_client, get_permissions):
        create_user(self.user_payload())
        response = get_permissions()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_can_inherit_its_group_permissions(self, create_user, api_client, create_group, get_permissions):
        response_user = create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response_group = create_group({'name': 'a'})
        response_permissions = get_permissions()
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

    def test_if_user_can_be_remove_its_group_permissions(self, create_user, api_client, create_group, get_permissions):
        response_user = create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response_group = create_group({'name': 'a'})
        response_permissions = get_permissions()
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
