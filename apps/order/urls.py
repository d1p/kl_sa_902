from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    OrderViewSet,
    OrderItemViewSet,
    OrderInviteViewSet,
    OrderItemInviteViewSet,
)

router = DefaultRouter()

router.register(
    "order-item-invite", OrderItemInviteViewSet, base_name="order-item-invite"
)
router.register("order-item", OrderItemViewSet, base_name="order-item")
router.register("order-invite", OrderInviteViewSet, base_name="order-invite")


router.register("order", OrderViewSet, base_name="order")

urlpatterns = [path("api/", include(router.urls))]
