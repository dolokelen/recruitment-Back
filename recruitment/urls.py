from django.urls import path, include
from rest_framework_nested import routers

from . import views
router = routers.DefaultRouter()

router.register('application-dates', views.ApplicationDateViewSet)

router.register('applicants', views.ApplicantViewSet)
router.register('applicant-documents', views.ApplicantDocumentViewSet)
router.register('applicant-address', views.ApplicantAddressViewSet)
router.register('applicant-contacts', views.ApplicantContactViewSet)
applicant_router = routers.NestedDefaultRouter(
    router, 'applicants', lookup='applicant')
# Only for GETTING applicant contacts.
applicant_router.register('contacts', views.ApplicantContactViewSet)

router.register('employees', views.EmployeeViewSet)
router.register('employee-documents', views.EmployeeDocumentViewSet)
router.register('employee-address', views.EmployeeAddressViewSet)
employee_router = routers.NestedDefaultRouter(
    router, 'employees', lookup='employee')
# Only for GETTING applicant contacts.
employee_router.register('contacts', views.EmployeeContactViewSet, basename='employee-contacts')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(applicant_router.urls)),
    path('', include(employee_router.urls)),
]
