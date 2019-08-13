from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ContactListSyncApiView, ContactGroupViewSet

router = DefaultRouter()

router.register("contact-group", ContactGroupViewSet, base_name="contact-group")

urlpatterns = [
    path("api/contact-list/", ContactListSyncApiView.as_view(), name="contact-list"),
    path("api/", include(router.urls)),
]
