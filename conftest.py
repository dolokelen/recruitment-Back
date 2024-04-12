import pytest
from rest_framework.test import APIClient


USER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEyOTY2NzY5LCJpYXQiOjE3MTI3OTM5NjksImp0aSI6IjdhNGNhYjg5NzVjZDQyMDM5ZGM2ZTM4NWUwNmQ5ODNkIiwidXNlcl9pZCI6MX0.m1aRcV_5sq8LkCLvyeoM8kHb3RZ3fI1e2tbxlh_3eoE'
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
def update(api_client):
    def do_update(endpoint, id, payload):
        return api_client.put(f'{endpoint}{id}/', payload)
    return do_update


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
