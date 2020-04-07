from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.order.invoice.views import InvoiceViewSet, TransactionVerifyViewSet, TransactionViewSet, invoice_view
from .views import (
    OrderViewSet,
    OrderItemViewSet,
    OrderInviteViewSet,
    OrderItemInviteViewSet,
    OrderParticipantViewSet,
    OrderRatingViewSet)

router = DefaultRouter()

router.register(
    "order-item-invite", OrderItemInviteViewSet, basename="order-item-invite"
)
router.register(
    "order-participant", OrderParticipantViewSet, basename="order-participant"
)
router.register("order-item", OrderItemViewSet, basename="order-item")
router.register("order-invite", OrderInviteViewSet, basename="order-invite")


router.register("order", OrderViewSet, basename="order")
router.register("order-rating", OrderRatingViewSet, basename="order_rating")

router.register("transaction", TransactionViewSet, basename="transaction")
router.register("invoice", InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/invoice-transaction-verification/",
        TransactionVerifyViewSet.as_view(),
        name="transaction_verification",
    ),
    path("invoice/view/<int:order_id>/", invoice_view, name="view_invoice")
]
