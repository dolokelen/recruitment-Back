from django.urls import path, include
from rest_framework_nested import routers

from . import views
router = routers.DefaultRouter()

router.register('application-dates', views.ApplicationDateViewSet)
router.register('applicants', views.ApplicantViewSet)
router.register('applicant-documents', views.ApplicantDocumentViewSet)

urlpatterns = [
    path('', include(router.urls))
]