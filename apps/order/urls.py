from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.order.invoice.views import InvoiceViewSet, TransactionVerifyViewSet, TransactionViewSet
from .views import (
    OrderViewSet,
    OrderItemViewSet,
    OrderInviteViewSet,
    OrderItemInviteViewSet,
    OrderParticipantViewSet,
)

router = DefaultRouter()

router.register(
    "order-item-invite", OrderItemInviteViewSet, base_name="order-item-invite"
)
router.register(
    "order-participant", OrderParticipantViewSet, base_name="order-participant"
)
router.register("order-item", OrderItemViewSet, base_name="order-item")
router.register("order-invite", OrderInviteViewSet, base_name="order-invite")


router.register("order", OrderViewSet, base_name="order")
router.register("transaction", TransactionViewSet, base_name="transaction")
router.register("invoice", InvoiceViewSet, base_name="invoice")

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/invoice-transaction-verification/",
        TransactionVerifyViewSet.as_view(),
        name="transaction_verification",
    ),
]
