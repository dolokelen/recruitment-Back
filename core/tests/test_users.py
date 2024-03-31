import pytest
from rest_framework import status
from model_bakery import baker

from core.models import User
from conftest import JWT, USER_TOKEN, user_payload, USERS_ENDPOINT


TOKEN_ENDPOINT = '/auth/jwt/create/'


@pytest.mark.django_db
class TestUser:
    """
    Anonymous users can send post request at this users user to register.
    """

    def test_if_anonymous_user_can_register_return_201(self, post):
        response = post(USERS_ENDPOINT, user_payload(email='m@gmail.com'))
        
        assert response.data['id'] > 0
        assert response.status_code == status.HTTP_201_CREATED

    def test_if_anonymous_user_cannot_retrieve_account_return_401(self, post, get):
        response = post(USERS_ENDPOINT, user_payload())
        response = get(USERS_ENDPOINT, response.data['id'])

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_registered_user_can_obtain_tokens_return_200(self, post):
        response_user = post(USERS_ENDPOINT, user_payload())
        email = user_payload().get('email')
        password = user_payload().get('password')
        response = post(TOKEN_ENDPOINT, {'email': email, 'password': password})

        assert response_user.data['id'] > 0
        assert response.data['access']
        assert response.data['refresh']
        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_can_retrieve_all_users_return_200(self, post, api_client, get_all):
        """
        This will enable me to get all users and display the appropriate profile.
        Perhaps the default behavior of the post() method is that it only returns
        the last resource that was created but since we can receive [{}] it confirms that we can get all
        """
        post(USERS_ENDPOINT, user_payload(email='j@gmail.com'))
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = get_all(USERS_ENDPOINT)

        assert response.data
        assert response.status_code == status.HTTP_200_OK

    def test_if_email_is_invalid_return_400(self, post):
        response = post(USERS_ENDPOINT, user_payload(email='dgmail.com'))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_payload_is_invalid_return_400(self, post):
        response = post(USERS_ENDPOINT, user_payload(password=''))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_email_exist_return_400(self, post):
        existing_user = baker.prepare(User)
        user = baker.make(User, email=existing_user.email)
        response = post(USERS_ENDPOINT, user_payload(email=user.email))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_password_length_is_less_than_8_chars_return_400(self, post):
        password = 'Djang@1'
        response = post(USERS_ENDPOINT, user_payload(
            password=password,
            confirm_password=password
        ))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_password_length_is_more_than_20_chars_return_400(self, post):
        password = 'Django123456789abcd*ef'
        response = post(USERS_ENDPOINT, user_payload(
            password=password,
            confirm_password=password
        ))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_password_does_not_contain_upper_letter_return_400(self, post):
        password = 'django!123'
        response = post(USERS_ENDPOINT, user_payload(
            password=password,
            confirm_password=password
        ))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_password_does_not_contain_lower_letter_return_400(self, post):
        password = '@DJANGO*!123'
        response = post(USERS_ENDPOINT, user_payload(
            password=password,
            confirm_password=password
        ))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_password_does_not_contain_number_return_400(self, post):
        password = '@Django*!#'
        response = post(USERS_ENDPOINT, user_payload(
            password=password,
            confirm_password=password
        ))

        assert response.status_code == status.HTTP_400_BAD_REQUEST
