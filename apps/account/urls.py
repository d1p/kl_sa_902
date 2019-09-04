from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView
from .customer.views import CustomerViewSet
from .restaurant.views import (
    RestaurantViewSet,
    RestaurantCategoryViewSet,
    RestaurantTableViewSet,
)
from .views import (
    MyTokenObtainPairView,
    ChangePasswordViewSet,
    ForgotPasswordViewSet,
    ResetPasswordViewSet,
    ResendVerificationViewSet,
    VerifyPhoneNumberViewSet,
    ChangePhoneNumberViewSet,
    ChangePhoneNumberVerificationViewSet,
    CheckResetTokenViewSet,
)

router = DefaultRouter()
router.register("account/fcm", FCMDeviceAuthorizedViewSet, basename="fcm")

router.register("account/customer", CustomerViewSet, basename="customer")
router.register("account/restaurant", RestaurantViewSet, basename="restaurant")
router.register(
    r"account/restaurant/category",
    RestaurantCategoryViewSet,
    base_name="restaurant-category",
)
router.register(
    r"restaurant-table", RestaurantTableViewSet, base_name="restaurant-table"
)
router.register(
    "account/change-password", ChangePasswordViewSet, base_name="change-password"
)
router.register(
    "account/forgot-password", ForgotPasswordViewSet, base_name="forgot-password"
)
router.register(
    "account/reset-password", ResetPasswordViewSet, base_name="reset-password"
)
router.register(
    "account/check-reset-token", CheckResetTokenViewSet, base_name="check-reset-token"
)

router.register(
    "account/resend-verification-code",
    ResendVerificationViewSet,
    base_name="resend-verification-code",
)
router.register(
    "account/change-phone-number",
    ChangePhoneNumberViewSet,
    base_name="change-phone-number",
)
router.register(
    "account/verify-phone-number",
    VerifyPhoneNumberViewSet,
    base_name="verify-phone-number",
)

router.register(
    "account/verify-new-phone-number",
    ChangePhoneNumberVerificationViewSet,
    base_name="verify-new-phone-number",
)

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
