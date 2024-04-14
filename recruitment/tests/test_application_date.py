import pytest
from django.contrib.auth.models import Permission
from rest_framework import status


TOKEN_ENDPOINT = '/auth/jwt/create/'
APPLICATION_DATE_ENDPOINT = '/recruitment/application-dates/'
GROUPS_ENDPOINT = '/core/groups/'
PERMISSIONS_ENDPOINT = '/core/permissions/'


@pytest.mark.django_db
class TestApplicationDate:
    """
    All views require authentication by REST_FRAMEWORK DEFAULT_PERMISSION_CLASSES SETTING.
    """

    def applicationdate_payload(self, open_year=2024, open_month=4, open_date=12, close_year=2024, close_moth=1, close_date=3):
        return {
            'open_year': open_year,
            'open_month': open_month,
            'open_date': open_date,
            'close_year': close_year,
            'close_month': close_moth,
            'close_date': close_date,
        }

    def test_if_permission_user_can_post_applicationdate_return_201(self, post, group_instance):
        data = self.applicationdate_payload()
        response = post(APPLICATION_DATE_ENDPOINT, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    def test_if_permission_user_can_get_applicationdate_return_200(self, post, get, group_instance):
        data = self.applicationdate_payload()
        response = post(APPLICATION_DATE_ENDPOINT, data)
        response = get(APPLICATION_DATE_ENDPOINT, response.data['id'])

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id']
    
    def test_if_permission_user_can_get_all_applicationdate_return_200(self, post, get_all, group_instance):
        data = self.applicationdate_payload()
        response = post(APPLICATION_DATE_ENDPOINT, data)
        response = get_all(APPLICATION_DATE_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK

    def test_if_permission_user_can_update_applicationdate_return_200(self, post, update, group_instance):
        response = post(APPLICATION_DATE_ENDPOINT,
                        self.applicationdate_payload())
        response = update(APPLICATION_DATE_ENDPOINT,
                          response.data['id'], self.applicationdate_payload(open_year=2025))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['open_year'] == 2025
    
    def test_if_permission_user_can_delete_applicationdate_return_204(self, post, delete, group_instance):
        response = post(APPLICATION_DATE_ENDPOINT,
                        self.applicationdate_payload())
        response = delete(APPLICATION_DATE_ENDPOINT, response.data['id'])

        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_if_partial_permission_user_cannot_update_applicationdate_return_403(self, post, update, group_instance):
        post_resp = post(APPLICATION_DATE_ENDPOINT,
                        self.applicationdate_payload())
        excluded_permission = Permission.objects.filter(
            name__in=['Can change application date'])
        group_instance.permissions.remove(*excluded_permission)
        response = update(APPLICATION_DATE_ENDPOINT,
                          post_resp.data['id'], self.applicationdate_payload(open_year=2025))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert post_resp.data['open_year'] != 2025
        assert post_resp.data['open_year'] == 2024
    
    def test_if_partial_permission_user_cannot_delete_applicationdate_return_403(self, post, delete, group_instance):
        post_resp = post(APPLICATION_DATE_ENDPOINT,
                        self.applicationdate_payload())
        excluded_permission = Permission.objects.filter(
            name__in=['Can delete application date'])
        group_instance.permissions.remove(*excluded_permission)
        response = delete(APPLICATION_DATE_ENDPOINT, post_resp.data['id'])

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert post_resp.data['id'] > 0

    def test_if_permissionless_user_cannot_post_applicationdate_return_403(self, post, group_instance):
        """
        Because they cannot post means they can't get, update or delete the resource.
        """
        excluded_permission = Permission.objects.filter(
            name__in=['Can add application date'])
        group_instance.permissions.remove(*excluded_permission)

        data = self.applicationdate_payload()
        response = post(APPLICATION_DATE_ENDPOINT, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_return_400(self, post, group_instance):
        data = self.applicationdate_payload(open_date='')
        response = post(APPLICATION_DATE_ENDPOINT, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
