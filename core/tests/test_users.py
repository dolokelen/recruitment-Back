from django.contrib.auth.models import Permission
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker

from core.models import User


@pytest.fixture
def create_user(api_client):
    def do_create_user(user_obj):
        return api_client.post('/auth/users/', user_obj)
    return do_create_user


@pytest.fixture
def login(api_client):
    def do_login_user(email_password):
        return api_client.post('/auth/jwt/create/', email_password)
    return do_login_user


@pytest.fixture
def get_users(api_client):
    def do_get_users():
        return api_client.get('/auth/users/')
    return do_get_users


@pytest.fixture
def get_user(api_client):
    def do_get_user(id):
        return api_client.get(f'/auth/users/{id}/')
    return do_get_user


token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExMzU1Mjc1LCJpYXQiOjE3MTExODI0NzUsImp0aSI6Ijk4ZmM5ZTBhYWIyNjQ3YzViM2Y2Y2UwZjY2ZWM2Yzc4IiwidXNlcl9pZCI6MX0.zKtwdAv7-6XdryhtKysYZAg3roin7uhRnyolepmrMNo'


@pytest.mark.django_db
class TestUser:
    """
    Anonymous users can send post request at this users endpoint to register.
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

    def test_if_anonymous_user_can_register_return_201(self, create_user):
        response = create_user(self.user_payload(email='m@gmail.com'))

        assert response.data['id'] > 0
        assert response.status_code == status.HTTP_201_CREATED

    def test_if_anonymous_user_cannot_retrieve_account_return_401(self, create_user, get_user):
        response = create_user(self.user_payload())
        response = get_user(response.data['id'])

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_registered_user_can_obtain_tokens_return_200(self, create_user, login):
        response_user = create_user(self.user_payload())
        email = self.user_payload().get('email')
        password = self.user_payload().get('password')
        response = login({'email': email, 'password': password})

        assert response_user.data['id'] > 0
        assert response.data['access']
        assert response.data['refresh']
        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_can_retrieve_all_users_return_200(self, create_user, api_client, get_users):
        """
        This will enable me to get all users and display the appropriate profile.
        Perhaps the default behavior of the post() method is that it only returns
        the last resource that was created but since we can receive [{}] it confirms that we can get all
        """
        create_user(self.user_payload())
        create_user(self.user_payload(email='j@gmail.com'))
        api_client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
        response = get_users()

        assert response.data
        assert response.status_code == status.HTTP_200_OK

    def test_if_email_is_invalid_return_400(self, create_user):
        response = create_user(self.user_payload(email='dgmail.com'))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_payload_is_invalid_return_400(self, create_user):
        response = create_user(self.user_payload(first_name=''))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_email_exist_return_400(self, create_user):
        existing_user = baker.prepare(User)
        user = baker.make(User, email=existing_user.email)
        response = create_user(self.user_payload(email=user.email))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.skip
    def test_if_password_length_is_less_than_8_chars_return_400(self, create_user):
        """
        I need to implementation logic for password in the serializer first.
        """
        response = create_user(self.user_payload())

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    @pytest.mark.skip
    def test_if_password_do_not_contain_upper_lower_number_return_400(self, create_user):
        """
        I need to implementation logic for password in the serializer first.
        """
        response = create_user(self.user_payload())

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    # I need to learn regular expression to validate the password
