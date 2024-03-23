import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from model_bakery import baker

from core.models import User


@pytest.fixture
def create_user(api_client):
    def do_create_user(user_obj):
        return api_client.post('/auth/users/', user_obj)
    return do_create_user


@pytest.mark.django_db
class TestCreateUser:
    """Test all necessary edge cases when creating users"""

    def create_user_obj(self, email='d@gmail.com', first_name='a', last_name='b',
                        password='Django123', confirm_password='Django123'):
        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'confirm_password': confirm_password
        }

    def test_if_data_is_valid_return_201(self, create_user):
        """We're not authenticating the email yet"""
        response = create_user(self.create_user_obj())

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_if_email_is_invalid_return_400(self, create_user):
        """Test should pass because the email is invalid"""
        response = create_user(self.create_user_obj(email='dgmail.com'))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_data_is_invalid_return_400(self, create_user):
        """All fields must be valid for this test to fail"""
        response = create_user(self.create_user_obj(first_name=''))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_user_is_anonymous_return_201(self, api_client, create_user):
        """Allow anonymous user to create account"""
        api_client.force_authenticate(user={})
        response = create_user(self.create_user_obj(email='m@gmail.com'))

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_if_email_exist_return_400(self, create_user):
        """Test will pass if the email addres already exist"""
        existing_user = baker.prepare(User)
        user = baker.make(User, email=existing_user.email)
        response = create_user(self.create_user_obj(email=user.email))

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRetrieveUser:

    def test_if_data_retrieval_successful_return_200(self, create_user):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExMTU5MDAwLCJpYXQiOjE3MTExNTU0MDAsImp0aSI6ImQyZTA1ZDU2Y2RmYjQwNjlhMmUyNjI1NmE5MzBlMDc3IiwidXNlcl9pZCI6MX0.16r7FE8v04MQSsiPMYCgTBgJpmoMFnScXe27aR0yqRs"
        response = create_user({
            'email': 'd@gmail.com',
            'first_name': 'a',
            'last_name': 'd',
            'password': 'd',
            'confirm_password': 'd'
        })

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        id = response.data['id']
        response = client.get(f'/auth/users/{id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_has_permission_to_retrieve_all_users(self):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExMTU5MDAwLCJpYXQiOjE3MTExNTU0MDAsImp0aSI6ImQyZTA1ZDU2Y2RmYjQwNjlhMmUyNjI1NmE5MzBlMDc3IiwidXNlcl9pZCI6MX0.16r7FE8v04MQSsiPMYCgTBgJpmoMFnScXe27aR0yqRs"
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = client.get(f'/auth/users/')
        
