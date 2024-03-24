import pytest
from django.contrib.auth.models import Group
from rest_framework import status
from model_bakery import baker
from model_bakery.recipe import seq

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
def get_all_groups(api_client):
    def do_get_all_groups():
        return api_client.get('/core/groups/')
    return do_get_all_groups


@pytest.fixture
def update_group(api_client):
    def do_update_group(payload, id):
        return api_client.put(f'/core/groups/{id}/', payload)
    return do_update_group


@pytest.fixture
def delete_group(api_client):
    def do_delete_group(id):
        return api_client.delete(f'/core/groups/{id}/')
    return do_delete_group


token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExMzU1Mjc1LCJpYXQiOjE3MTExODI0NzUsImp0aSI6Ijk4ZmM5ZTBhYWIyNjQ3YzViM2Y2Y2UwZjY2ZWM2Yzc4IiwidXNlcl9pZCI6MX0.zKtwdAv7-6XdryhtKysYZAg3roin7uhRnyolepmrMNo'


@pytest.mark.django_db
class TestGroup:
    """
        Anonymous users can't retrieve group so they can't perform 
        put or delete request becasue one must get a group_id before...
    """

    def user_payload(self, email='d@gmail.com', first_name='a', last_name='b',
                     password='Django123', confirm_password='Django123'):
        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'confirm_password': confirm_password
        }

    def test_if_authenticated_user_can_create_group_return_201(self, create_user, api_client, create_group):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_group_payload_is_invalid_return_400(self, create_user, api_client, create_group):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_group_payload_exists_return_400(self, create_user, api_client, create_group):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        response = create_group({'name': response.data['name']})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_anonymous_user_cannot_create_group_return_401(self, create_user, api_client, create_group):
        create_user(self.user_payload())
        response = create_group({'name': 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_authenticated_user_can_retrieve_a_group_return_200(self, create_user, api_client, create_group, get_group):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        response = get_group(response.data['id'])

        assert response.data['id'] > 0
        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_can_retrieve_groups_return_200(self, create_user, api_client, create_group, get_all_groups):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        response = get_all_groups()

        assert response.status_code == status.HTTP_200_OK

    def test_if_anonymous_user_cannot_retrieve_group_return_401(self, create_user, get_all_groups, api_client):
        create_user(self.user_payload())
        response = get_all_groups()
        api_client.credentials()  # no credentials provided

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_authenticated_user_can_update_group_name_return_200(self, create_user, api_client, create_group, get_group, update_group):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        response = get_group(response.data['id'])
        response = update_group({'name': 'b'}, response.data['id'])

        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_can_delete_group_return_204(self, create_user, api_client, create_group, delete_group, get_group):
        create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = create_group({'name': 'a'})
        response = get_group(response.data['id'])
        response = delete_group(response.data['id'])

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_if_user_can_be_added_to_a_group(self, create_user, api_client, create_group):
        response_user = create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response_group = create_group({'name': 'a'})
        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=[response_group.data['id']]).values_list('id', flat=True)
        user_instance.groups.add(*queryset)

        assert len(user_instance.groups.all()) == len(queryset)

    def test_if_user_can_be_removed_from_a_group(self, create_user, api_client, create_group):
        response_user = create_user(self.user_payload())
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response_group = create_group({'name': 'a'})
        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=[response_group.data['id']]).values_list('id', flat=True)
        user_instance.groups.remove(*queryset)

        assert len(user_instance.groups.all()) < len(queryset)
        assert len(user_instance.groups.all()) == 0

    def test_if_user_can_be_added_to_groups(self, create_user, api_client, create_group):
        response_user = create_user(self.user_payload())
        groups = [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        groups_ids = [create_group({'name': group.get('name')}).data['id'] for group in groups]
        
        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=groups_ids).values_list('id', flat=True)
        user_instance.groups.add(*queryset)

        assert len(user_instance.groups.all()) == len(groups_ids)
        assert len(user_instance.groups.all()) == len(queryset)
    
    def test_if_user_can_be_removed_from_groups(self, create_user, api_client, create_group):
        response_user = create_user(self.user_payload())
        groups = [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)

        groups_ids = [create_group({'name': group.get('name')}).data['id'] for group in groups]
        
        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=groups_ids).values_list('id', flat=True)
        user_instance.groups.add(*queryset)

        user_instance.groups.remove(*queryset[:2])
        assert len(user_instance.groups.all()) < len(groups_ids)
        assert len(user_instance.groups.all()) < len(queryset)