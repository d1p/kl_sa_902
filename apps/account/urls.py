from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .customer.views import CustomerViewSet
from .views import MyTokenObtainPairView

router = DefaultRouter()
router.register("account/fcm", FCMDeviceAuthorizedViewSet, basename="fcm")

router.register("account/customer", CustomerViewSet, basename="customer")

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/auth/api-token-auth/",
        MyTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/auth/api-token-refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
]
