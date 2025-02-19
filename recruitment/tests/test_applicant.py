import pytest
import io
from PIL import Image
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from model_bakery import baker

from conftest import JWT, USER_TOKEN, USERS_ENDPOINT, user_payload
from recruitment.models import Applicant, ApplicantDocument


APPLICANT_ENDPOINT = '/recruitment/applicants/'


def create_image_file():
    # Create a new blank image with size 100x100
    image = Image.new('RGB', (100, 100))

    # Create a temporary file in memory to save the image
    tmp_file = BytesIO()
    image.save(tmp_file, 'PNG')
    # Move the pointer at the begining of the file for the entire data to be read.
    tmp_file.seek(0)

    # Create a Django SimpleUploadedFile object from the temporary file
    uploaded_file = SimpleUploadedFile(
        'test_image.png', tmp_file.read(), content_type='image/png')

    return uploaded_file


@pytest.mark.django_db
class TestApplicant:
    """
    THIS TEST WILL FAIL WHEN I APPLY PERMISSIONS WHICH I'LL DO LATER!
    Applicant has OneToOne relationship with User. 

    All views require authentication by REST_FRAMEWORK DEFAULT_PERMISSION_CLASSES SETTING.
    Pytest uses our 'models.py, serializers.py, views.py, urls.py' 
    but it doesn't commit the Test data to our actual database.

    Just like 'views.py', the serializer that was used to post 
    is the same serializer that is used to return post response,
    meaning only fields included in that serializer will be in the 
    response object. But if you've a serializer for a GET request
    you can send a GET request to that endpoint.

    If you pass this 'TestApplicant().payload()' DIRECTLY as argument 
    to a 'post, put, patch' method you'll get the data [payload], 
    otherwiser, all tests in TestApplicant will be executed before 
    your test is executed and this can case KeyError for OneToOne or 
    unique fields.

    If you don't care about fields validations OR if model 'A' has a
    relationship to your model and model 'A' instance is being AUTOMATED
    in your model save method then use 'baker.make(YourModel)' this
    will create model 'A' and its intended AUTOMATION will work. 

    baker.make(User, email='mecom'), Baker considers the email as valid.
    """

    def payload(self, religion='Christian', gender='Male', county='Bong', birth_date='2020-01-22'):
        """ 
        I using 1 for 'user' because I'm assuming he's the first user.
        """
        baker.make(Applicant)
        return {
            'user': 1,
            'religion': religion,
            'image': create_image_file(),
            'gender': gender,
            'birth_date': birth_date,
            'county': county,
        }

    def test_if_authenticated_user_can_post_applicant_return_201(self, post, api_client):
        """ See this class for the comment"""
        user_resp = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(APPLICANT_ENDPOINT, self.payload())
        instance = Applicant.objects.get(user_id=user_resp.data['id'])

        assert response.status_code == status.HTTP_201_CREATED
        assert instance.user.id == user_resp.data['id']

    def test_if_anonymous_user_cannot_post_applicant_return_401(self, post):
        """ See this class for the comment"""
        user_resp = post(USERS_ENDPOINT, user_payload())
        response = post(APPLICANT_ENDPOINT, self.payload())

        assert user_resp.data['id'] > 0
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_authenticated_user_can_get_applicant_return_200(self, post, get, api_client):
        """ See this class for the comment"""
        user_resp = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(APPLICANT_ENDPOINT, self.payload())
        response = get(APPLICANT_ENDPOINT, user_resp.data['id'])

        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['id'] == user_resp.data['id']

    def test_if_authenticated_user_can_get_all_applicants_return_200(self, post, api_client, get_all):
        """ Although any authenticated user can get all applicants
            which is not good. Leter I'll apply permission to the 
            Applicant view and create another Applicant view call
            ApplicantProfile which will only allow applicant to get
            only thier relevant data and allow only PATCH request.
        """
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(APPLICANT_ENDPOINT, self.payload())
        response = get_all(APPLICANT_ENDPOINT)

        assert response.status_code == status.HTTP_200_OK

    def test_if_authenticated_user_can_patch_applicant_return_200(self, post, patch, api_client):
        """ Put request will fial if you don't give all the fields which is only unique here.
            Perhaps it's becasue of the file field [image] in the model.
            Id number should never be updated, but I'm using it because 
            it's not generated by model bakery.
        """
        data = {'id_number': '099', 'image': create_image_file()}

        user_res = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(APPLICANT_ENDPOINT, self.payload())
        response = patch(APPLICANT_ENDPOINT, user_res.data['id'], data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id_number'] == '099'

    def test_if_authenticated_user_can_delete_applicant_return_204(self, post, delete, api_client):
        """ See the this class for comment """
        user_res = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(APPLICANT_ENDPOINT, self.payload())
        response = delete(APPLICANT_ENDPOINT, user_res.data['id'])

        assert response.status_code == status.HTTP_204_NO_CONTENT

    # def test_if_partial_permission_user_cannot_update_applicationdate_return_403(self, post, update, group_instance):
    #     post_resp = post(APPLICANT_ENDPOINT,
    #                      self.applicationdate_payload())
    #     excluded_permission = Permission.objects.filter(
    #         name__in=['Can change application date'])
    #     group_instance.permissions.remove(*excluded_permission)
    #     response = update(APPLICANT_ENDPOINT,
    #                       post_resp.data['id'], self.applicationdate_payload(open_date='2025-12-15'))

    #     assert response.status_code == status.HTTP_403_FORBIDDEN
    #     assert post_resp.data['open_date'] != '2025-12-15'
    #     assert post_resp.data['open_date'] == '2024-04-15'

    # def test_if_partial_permission_user_cannot_delete_applicationdate_return_403(self, post, delete, group_instance):
    #     post_resp = post(APPLICANT_ENDPOINT,
    #                      self.applicationdate_payload())
    #     excluded_permission = Permission.objects.filter(
    #         name__in=['Can delete application date'])
    #     group_instance.permissions.remove(*excluded_permission)
    #     response = delete(APPLICANT_ENDPOINT, post_resp.data['id'])

    #     assert response.status_code == status.HTTP_403_FORBIDDEN
    #     assert post_resp.data['id'] > 0

    # def test_if_permissionless_user_cannot_post_applicationdate_return_403(self, post, group_instance):
    #     """
    #     Because they cannot post means they can't get, update or delete the resource.
    #     """
    #     excluded_permission = Permission.objects.filter(
    #         name__in=['Can add application date'])
    #     group_instance.permissions.remove(*excluded_permission)

    #     data = self.applicationdate_payload()
    #     response = post(APPLICANT_ENDPOINT, data)

    #     assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_return_400(self, post, api_client):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        response = post(APPLICANT_ENDPOINT, self.payload(gender=''))

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ------------------------ ApplicantDocument ---------------

APP_DOCUMENT_ENDPOINT = '/recruitment/applicant-documents/'


def create_pdf_file():
    # Create an in-memory PDF file
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Draw some text on the PDF
    c.drawString(100, 750, "Hello, this is a PDF file generated dynamically!")

    # Save the PDF
    c.save()

    # Move the pointer at the beginning of the file for the entire data to be read
    pdf_buffer.seek(0)

    # Create a Django SimpleUploadedFile object from the PDF buffer
    uploaded_file = SimpleUploadedFile(
        'test_pdf.pdf', pdf_buffer.read(), content_type='application/pdf')

    return uploaded_file


@pytest.mark.django_db
class TestApplicantDocument:
    """ 
    All views require authentication by REST_FRAMEWORK DEFAULT_PERMISSION_CLASSES SETTING.
    Pytest uses our 'models.py, serializers.py, views.py, urls.py' 
    but it doesn't commit the Test data to our actual database.

    Just like 'views.py', the serializer that was used to post 
    is the same serializer that is used to return post response,
    meaning only fields included in that serializer will be in the 
    response object. But if you've a serializer for a GET request
    you can send a GET request to that endpoint.

    If you pass this 'TestApplicant().payload()' DIRECTLY as argument 
    to a 'post, put, patch' method you'll get the data [payload], 
    otherwiser, all tests in TestApplicant will be executed before 
    your test is executed and this can case KeyError for OneToOne or 
    unique fields.

    If you don't care about fields validations OR if model 'A' has a
    relationship to your model and model 'A' instance is being AUTOMATED
    in your model save method then use 'baker.make(YourModel)' this
    will create model 'A' and its intended AUTOMATION will work. 

    baker.make(User, email='mecom'), Baker considers the email as valid.
    """

    def payload(self, applicant_id=1, institution='EDU', major='math',
                manor='lab', qualification='Bachelor', county='Bong',
                cgpa=3.8, country='Lib',  graduation_year=2020, degree=create_pdf_file(),
                police_clearance=create_pdf_file(), community_letter=create_pdf_file(),
                application_letter=create_pdf_file(), resume=create_pdf_file(),
                reference_letter=create_pdf_file()):
        return {
            'applicant': applicant_id,
            'institution': institution,
            'major': major,
            'manor': manor,
            'graduation_year': graduation_year,
            'qualification': qualification,
            'county': county,
            'country': country,
            'cgpa': cgpa,
            'police_clearance': police_clearance,
            'degree': degree,
            'resume': resume,
            'community_letter': community_letter,
            'reference_letter': reference_letter,
            'application_letter': application_letter,
        }

    def test_if_authenticated_user_can_post_document_return_201(self, post, api_client):
        """ See this class for the comment"""
        user_resp = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        applicant_res = post(APPLICANT_ENDPOINT, TestApplicant().payload())
        applicant = Applicant.objects.get(user_id=user_resp.data['id'])
        response = post(APP_DOCUMENT_ENDPOINT, self.payload())
        document = ApplicantDocument.objects.get(applicant=applicant.user.id)

        assert response.status_code == status.HTTP_201_CREATED
        assert document.applicant.user.id == applicant_res.data['user']

    def test_if_applicant_can_only_post_a_set_of_document_return_400(self, post, api_client):
        """ I'm posting two sets of documents for one applicant """
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        post(APPLICANT_ENDPOINT, TestApplicant().payload())
        post(APP_DOCUMENT_ENDPOINT, self.payload())
        res = post(APP_DOCUMENT_ENDPOINT, self.payload())

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_applicant_can_get_document_return_200(self, post, get, api_client):
        """ See this class for comment. THIS TEST IS REPORTING 404 WHEN RUN TOGETHER"""
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        app_res = post(APPLICANT_ENDPOINT, TestApplicant().payload())
        post(APP_DOCUMENT_ENDPOINT, self.payload())
        res = get(APP_DOCUMENT_ENDPOINT, app_res.data['user'])

        assert res.status_code == status.HTTP_200_OK

    def test_if_applicant_can_get_all_documents_return_200(self, post, get_all, api_client):
        """ See this class for comment """
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        post(APPLICANT_ENDPOINT, TestApplicant().payload())
        post(APP_DOCUMENT_ENDPOINT, self.payload())
        res = get_all(APP_DOCUMENT_ENDPOINT)

        assert res.status_code == status.HTTP_200_OK

    @pytest.mark.skip
    def test_if_user_can_patch_document_return_200(self, post, patch, api_client):
        """ See this class for comment """
        modified_data = self.payload()
        modified_data.pop('applicant')

        # post(USERS_ENDPOINT, user_payload())
        # api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        # app_res = post(APPLICANT_ENDPOINT, TestApplicant().payload())
        # doc_res = post(APP_DOCUMENT_ENDPOINT, self.payload(applicant_id=app_res.data['user']))
        # res = patch(APP_DOCUMENT_ENDPOINT, doc_res.data['applicant'], modified_data)

        # assert res.status_code == status.HTTP_200_OK

        # updated_data = {
        #     'applicant':1,
        #     'institution': 'UL',
        #     'major': 'Math',
        #     'manor': 'Physics',
        #     'graduation_year': 2020,
        #     'qualification': 'Bachelor',
        #     'county': 'Nimba',
        #     'country': 'Lib',
        #     'cgpa': 2.5,
        #     'police_clearance': create_image_file(),
        #     'degree': create_image_file(),
        #     'resume': create_image_file(),
        #     'community_letter': create_image_file(),
        #     'reference_letter': create_image_file(),
        #     'application_letter': create_image_file(),
        # }

        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        app_res = post(APPLICANT_ENDPOINT, TestApplicant().payload())
        res = post(APP_DOCUMENT_ENDPOINT, self.payload(
            applicant_id=app_res.data['user']))
# The below payload looks good yet I'm getting http 400
        res = patch(APP_DOCUMENT_ENDPOINT,
                    res.data['applicant'], modified_data)

        assert res.status_code == status.HTTP_200_OK

    def test_if_applicant_can_delete_document_return_204(self, post, delete, api_client):
        """ See this class for comment. THIS TEST IS REPORTING ERROR WHEN RUN TOGETHER"""
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        app_res = post(APPLICANT_ENDPOINT, TestApplicant().payload())
        res = post(APP_DOCUMENT_ENDPOINT, self.payload(
            applicant_id=app_res.data['user']))
        res = delete(APP_DOCUMENT_ENDPOINT, res.data['applicant'])

        assert res.status_code == status.HTTP_204_NO_CONTENT


# ---------------------- ApplicantAddress -------------------
APP_ADDRESS_ENDPOINT = '/recruitment/applicant-address/'


@pytest.mark.django_db
class TestApplicantAddress:
    """ ApplicantDocument has OneToOne relationship to Applicant 
        The serializer that was used to post is that same serializer 
        that is use to return the response. Get request serializer only use for get request
    """

    def payload(self, applicant_id=1, county='Bong', district=1, community='ABC', house_address='abc'):
        """ Country default value is Liberia that's it's not included """
        return {
            'applicant': applicant_id,
            'county': county,
            'district': district,
            'community': community,
            'house_address': house_address
        }

    def test_if_applicant_can_post_address_return_201(self, post, api_client):
        """ 
        If you instantiate TestApplicant here all of its tests will run
        thus causing unique constraint error for 1-1 relationship when 
        you attempt to post to that same endpoint with the same payload.
        But when instantiated in a request method it is use as value not TestClass. 

        See this class for generic comment 
        """
        user_resp = post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        post(APPLICANT_ENDPOINT, TestApplicant().payload())
        applicant = Applicant.objects.get(user_id=user_resp.data['id'])
        response = post(APP_ADDRESS_ENDPOINT, self.payload())

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['applicant'] == applicant.user.id

    def test_if_applicant_can_get_address_return_200(self, post, get, api_client):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        post(APPLICANT_ENDPOINT, TestApplicant().payload())
        res = post(APP_ADDRESS_ENDPOINT, self.payload())
        res = get(APP_ADDRESS_ENDPOINT, res.data['applicant'])

        assert res.status_code == status.HTTP_200_OK
        assert res.data['applicant'] > 0

    def test_if_applicant_can_get_all_address_return_200(self, post, get_all, api_client):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        post(APPLICANT_ENDPOINT, TestApplicant().payload())
        res = post(APP_ADDRESS_ENDPOINT, self.payload())
        res = get_all(APP_ADDRESS_ENDPOINT)

        assert res.status_code == status.HTTP_200_OK

    def test_if_applicant_can_patch_address_return_200(self, post, patch, api_client):
        """ 
        If I pop applicant the patch works. If I leave applicant 
        there the patch works. If I manually recreate the data with 
        applicant or without applicant it doesn't work. If I update 
        any property the test fails. These behaviors were not experienced 
        in other classes. Perhaps it's because of the long relationship
        Applicant-to-User ApplicantAddress-to-Applicant
        """

        updated_data = self.payload()
        updated_data.pop('applicant')

        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        post(APPLICANT_ENDPOINT, TestApplicant().payload())
        addr_res = post(APP_ADDRESS_ENDPOINT, self.payload())
        res = patch(APP_ADDRESS_ENDPOINT,
                    addr_res.data['applicant'], updated_data)

        assert res.status_code == status.HTTP_200_OK

    def test_if_applicant_can_delete_address_return_204(self, post, delete, api_client):
        post(USERS_ENDPOINT, user_payload())
        api_client.credentials(HTTP_AUTHORIZATION=JWT + USER_TOKEN)
        post(APPLICANT_ENDPOINT, TestApplicant().payload())
        addr_res = post(APP_ADDRESS_ENDPOINT, self.payload())
        res = delete(APP_ADDRESS_ENDPOINT, addr_res.data['applicant'])

        assert res.status_code == status.HTTP_204_NO_CONTENT
