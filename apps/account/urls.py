from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView
from .customer.views import CustomerViewSet, MiscViewSet
from .restaurant.views import (
    RestaurantViewSet,
    RestaurantCategoryViewSet,
    RestaurantTableViewSet,
    report_view)
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
router.register("account/customer-misc", MiscViewSet, basename="customer-misc")
router.register(
    r"account/restaurant/category",
    RestaurantCategoryViewSet,
    basename="restaurant-category",
)
router.register("account/restaurant", RestaurantViewSet, basename="restaurant")
router.register(
    r"restaurant-table", RestaurantTableViewSet, basename="restaurant-table"
)
router.register(
    "account/change-password", ChangePasswordViewSet, basename="change-password"
)
router.register(
    "account/forgot-password", ForgotPasswordViewSet, basename="forgot-password"
)
router.register(
    "account/reset-password", ResetPasswordViewSet, basename="reset-password"
)
router.register(
    "account/check-reset-token", CheckResetTokenViewSet, basename="check-reset-token"
)

router.register(
    "account/resend-verification-code",
    ResendVerificationViewSet,
    basename="resend-verification-code",
)
router.register(
    "account/change-phone-number",
    ChangePhoneNumberViewSet,
    basename="change-phone-number",
)
router.register(
    "account/verify-phone-number",
    VerifyPhoneNumberViewSet,
    basename="verify-phone-number",
)

router.register(
    "account/verify-new-phone-number",
    ChangePhoneNumberVerificationViewSet,
    basename="verify-new-phone-number",
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
    path("account/restaurant/report/<int:user_id>/", report_view, name="report_view"),

]
