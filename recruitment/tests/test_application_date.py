import pytest
from django.contrib.auth.models import Group, Permission
from rest_framework import status

from conftest import (
    JWT, USER_TOKEN, user_payload,
    USERS_ENDPOINT
)
from core.models import User


TOKEN_ENDPOINT = '/auth/jwt/create/'
APPLICATION_DATE_ENDPOINT = '/recruitment/application-dates/'
GROUPS_ENDPOINT = '/core/groups/'
PERMISSIONS_ENDPOINT = '/core/permissions/'


@pytest.mark.django_db
class TestUser:
    """
    Anonymous users cannot perform any CRUD operations on any recruitment views.
    """

    def application_date_payload(self, open_year=2024, open_month=4, open_date=12, close_year=2024, close_moth=1, close_date=3):
        return {
            'open_year': open_year,
            'open_month': open_month,
            'open_date': open_date,
            'close_year': close_year,
            'close_month': close_moth,
            'close_date': close_date,
        }

    def test_if_unauthorize_user_cannot_post_application_date_return_403(self, post, group_instance):
        excluded_permissions = Permission.objects.filter(
            name__in=['Can add application date'])
        group_instance.permissions.remove(*excluded_permissions)

        response = post(APPLICATION_DATE_ENDPOINT,
                        self.application_date_payload())

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_return_401(self, post, group_instance):
        # The validation for the year is not holding!!!!
        data = self.application_date_payload(open_date=202)
        response = post(APPLICATION_DATE_ENDPOINT, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
