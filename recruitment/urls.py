from django.urls import path, include
from rest_framework_nested import routers

from . import views
router = routers.DefaultRouter()

router.register('application-dates', views.ApplicationDateViewSet)
router.register('application-stages', views.QualifyApplicantViewSet)

router.register('applicant-screenings', views.ApplicantScreeningViewSet, basename='app-screenings')
router.register('applicants', views.ApplicantViewSet, basename='apps')
router.register('applicant-documents', views.ApplicantDocumentViewSet)
router.register('applicant-address', views.ApplicantAddressViewSet)
router.register('applicant-contacts', views.ApplicantContactViewSet)
router.register('applicant-profile',
                views.ApplicantProfileViewSet, basename='app-profile')
applicant_router = routers.NestedDefaultRouter(
    router, 'applicants', lookup='applicant')
# Only for GETTING applicant contacts.
applicant_router.register('contacts', views.ApplicantContactViewSet)

router.register('employees', views.EmployeeViewSet)
router.register('employee-documents', views.EmployeeDocumentViewSet)
router.register('employee-address', views.EmployeeAddressViewSet)
router.register('employee-supervisors', views.EmployeeSupervisorViewSet, basename='emp-supervisors')
router.register('employee-profile',
                views.EmployeeProfileViewSet, basename='emp-profile')
employee_router = routers.NestedDefaultRouter(
    router, 'employees', lookup='employee')
# Only for GETTING applicant contacts.
employee_router.register(
    'contacts', views.EmployeeContactViewSet, basename='employee-contacts')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(applicant_router.urls)),
    path('', include(employee_router.urls)),
]
