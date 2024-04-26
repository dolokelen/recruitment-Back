import pytest
from django.contrib.auth.models import Group
from rest_framework import status

from core.models import User
from conftest import JWT, USER_TOKEN, USERS_ENDPOINT, user_payload


GROUPS_ENDPOINT = '/core/groups/'


@pytest.mark.django_db
class TestGroup:
    """
    Anonymous users can't retrieve group so they can't perform 
    put or delete request becasue one must get a group_id before...
    If you don't want field validation use Model Baker else add the fields manually.
    baker.make(User, email='mecom'), Baker considers the email as valid.
    """

    def test_if_authenticated_user_can_create_group_return_201(self, post, api_client):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_group_payload_is_invalid_return_400(self, post, api_client):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_group_payload_exists_return_400(self, post, api_client):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        response = post(GROUPS_ENDPOINT, {'name': response.data['name']})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_anonymous_user_cannot_create_group_return_401(self, post):
        post(USERS_ENDPOINT, user_payload())
        response = post(GROUPS_ENDPOINT, {'name': 'a'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_authenticated_user_can_retrieve_a_group_return_200(self, post, api_client, get):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        response = get(GROUPS_ENDPOINT, response.data['id'])

        assert response.data['id'] > 0
        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_can_retrieve_groups_return_200(self, post, api_client, get_all):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        response = get_all(GROUPS_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK

    def test_if_anonymous_user_cannot_retrieve_group_return_401(self, post, get_all, api_client):
        post(USERS_ENDPOINT, user_payload())
        response = get_all(GROUPS_ENDPOINT)
        api_client.credentials()  # no credentials provided

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_authenticated_user_can_update_group_name_return_200(self, post, api_client, get, put):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        response = get(GROUPS_ENDPOINT, response.data['id'])
        response = put(GROUPS_ENDPOINT, response.data['id'], {'name': 'b'})

        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_can_delete_group_return_204(self, post, api_client, delete, get):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(GROUPS_ENDPOINT, {'name': 'a'})
        response = get(GROUPS_ENDPOINT, response.data['id'])
        response = delete(GROUPS_ENDPOINT, response.data['id'])

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_if_user_can_be_added_to_a_group(self, post, api_client):
        response_user = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response_group = post(GROUPS_ENDPOINT, {'name': 'a'})
        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=[response_group.data['id']]).values_list('id', flat=True)
        user_instance.groups.add(*queryset)

        assert len(user_instance.groups.all()) == len(queryset)

    def test_if_user_can_be_removed_from_a_group(self, post, api_client):
        response_user = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response_group = post(GROUPS_ENDPOINT, {'name': 'a'})
        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=[response_group.data['id']]).values_list('id', flat=True)
        user_instance.groups.remove(*queryset)

        assert len(user_instance.groups.all()) < len(queryset)
        assert len(user_instance.groups.all()) == 0

    def test_if_user_can_be_added_to_groups(self, post, api_client):
        response_user = post(USERS_ENDPOINT, user_payload())
        groups = [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)

        groups_ids = [post(GROUPS_ENDPOINT,
                           {'name': group.get('name')}).data['id'] for group in groups]

        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=groups_ids).values_list('id', flat=True)
        user_instance.groups.add(*queryset)

        assert len(user_instance.groups.all()) == len(groups_ids)
        assert len(user_instance.groups.all()) == len(queryset)

    def test_if_user_can_be_removed_from_groups(self, post, api_client):
        response_user = post(USERS_ENDPOINT, user_payload())
        groups = [{'name': 'a'}, {'name': 'b'}, {'name': 'c'}]
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)

        groups_ids = [post(GROUPS_ENDPOINT,
                           {'name': group.get('name')}).data['id'] for group in groups]

        user_instance = User.objects.get(id=response_user.data['id'])
        queryset = Group.objects.filter(
            id__in=groups_ids).values_list('id', flat=True)
        user_instance.groups.add(*queryset)

        user_instance.groups.remove(*queryset[:2])
        assert len(user_instance.groups.all()) < len(groups_ids)
        assert len(user_instance.groups.all()) < len(queryset)
