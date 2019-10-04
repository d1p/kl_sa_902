from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.notification.views import ActionViewSet

router = DefaultRouter()
router.register("notification", ActionViewSet, basename="notification-list")

urlpatterns = [path("api/", include(router.urls))]
