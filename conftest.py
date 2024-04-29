import pytest
from rest_framework.test import APIClient

# This access token has to be superuser. User will NOT have superuser status.
USER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE0NTM1NzU3LCJpYXQiOjE3MTQzNjI5NTcsImp0aSI6IjI3MWRiMzYyN2ZhNjRlNDM4ZDFhNDJhZmQ2NGMwMzExIiwidXNlcl9pZCI6MX0.sww4HGLDl8n76B0zWFLsv--CY4ryUxfHgPrGmg0JAZM'

JWT = 'JWT '
USERS_ENDPOINT = '/auth/users/'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def post(api_client):
    def post(endpoint, obj):
        return api_client.post(endpoint, obj)
    return post


@pytest.fixture
def get_all(api_client):
    def do_get_all(endpoint):
        return api_client.get(endpoint)
    return do_get_all


@pytest.fixture
def get(api_client):
    def do_get(endpoint, id):
        return api_client.get(f'{endpoint}{id}/')
    return do_get


@pytest.fixture
def put(api_client):
    def do_put(endpoint, id, payload):
        return api_client.put(f'{endpoint}{id}/', payload)
    return do_put


@pytest.fixture
def patch(api_client):
    def do_patch(endpoint, id, payload):
        return api_client.patch(f'{endpoint}{id}/', payload)
    return do_patch


@pytest.fixture
def delete(api_client):
    def do_delete(endpoint, id):
        return api_client.delete(f'{endpoint}{id}/')
    return do_delete


def user_payload(email='d@gmail.com', first_name='a', last_name='b',
                 password='Django@123', confirm_password='Django@123'):
    return {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'password': password,
        'confirm_password': confirm_password
    }


@pytest.fixture
def group_instance(post, get, get_all, api_client):
    from django.contrib.auth.models import Group
    from core.models import User

    GROUPS_ENDPOINT = '/core/groups/'
    PERMISSIONS_ENDPOINT = '/core/permissions/'
    user_resp = post(USERS_ENDPOINT, user_payload())
    api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
    group_resp = post(GROUPS_ENDPOINT, {'name': 'a'})
    group_get_resp = get(GROUPS_ENDPOINT, group_resp.data['id'])

    # Add user to group
    user_instance = User.objects.get(id=user_resp.data['id'])
    queryset = Group.objects.filter(
        id__in=[group_resp.data['id']]).values_list('id', flat=True)
    user_instance.groups.add(*queryset)

    # Assign permissions to group
    group_instance = Group.objects.get(id=group_get_resp.data['id'])
    permissions_res = get_all(PERMISSIONS_ENDPOINT)
    permissions = permissions_res.json()  # b/c the response is a byte

    for permission in permissions:
        group_instance.permissions.add(permission['id'])

    return group_instance
