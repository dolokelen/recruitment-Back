import pytest
from rest_framework.test import APIClient


USER_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExNjA3Njg5LCJpYXQiOjE3MTE0MzQ4ODksImp0aSI6ImZkMTBjNTM4MWVhNTRhMDQ4YjczMTJjOTg1ZDQ1NjNjIiwidXNlcl9pZCI6MX0.rR4GB4KK8ru57Hilha3Lr66prl5g9pcJ9HyBSSmXO60'
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
