from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.account.types import ProfileType
from apps.order.invoice.filters import InvoiceFilter
from apps.order.invoice.tasks import (
    send_all_bill_paid_notification,
    send_single_bill_paid_notification,
)
from apps.order.invoice.types import PaymentStatus
from apps.order.invoice.utils import verify_transaction, capture_transaction
from apps.order.models import Order
from apps.order.tasks import send_new_order_items_confirmed_notification
from apps.order.types import OrderType, OrderStatusType
from .models import Invoice, Transaction
from .serializers import (
    InvoiceSerializer,
    TransactionVerifySerializer,
    TransactionSerializer,
)


class InvoiceViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = InvoiceSerializer
    lookup_field = "order"
    filter_backends = [DjangoFilterBackend]
    filterset_class = InvoiceFilter

    def get_queryset(self):
        user = self.request.user
        if user.profile_type == ProfileType.CUSTOMER:
            queryset = Invoice.objects.filter(order__order_participants__user=user)
        elif user.profile_type == ProfileType.RESTAURANT:
            queryset = Invoice.objects.filter(order__restaurant=user)
        else:
            queryset = Invoice.objects.all()

        return queryset


class TransactionVerifyViewSet(CreateAPIView):
    """ Check if a payment has completed, request with the "transaction_id" returned by paytabs SDK.
    **NOTE: This api is only to be used for syncing transactions with paytabs and the server.
    Please verify and show error messages for the payment related issue using the paytabs SDK.**
    request example:
    ```json
        {
            "transaction_id": "89342389bfjsdbf"
        }
    ```
    returns HTTP 200 if everything is ok, with the response content
    returns HTTP 200 with *transaction_status*
    ```json
        {"transaction_status": 2}
    ```
    This route is also used by paytabs webhook service, so if for some reasons mobile application can not connect with
    the internet, the transaction is proceed.
    Statuses for payment statuses:
    ```python
    PENDING = 0
    SUCCESSFUL = 1
    FAILED = 2
    INVALID = 3```
    """

    permission_classes = [AllowAny]
    serializer_class = TransactionVerifySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print("Transaction_ID " + serializer.validated_data.get("transaction_id"))
        response_data = verify_transaction(
            serializer.validated_data.get("transaction_id")
        )
        print(f"response from paytabs {response_data}")
        try:
            transaction = Transaction.objects.get(
                pt_order_id=response_data.get("order_id")
            )
        except Transaction.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if transaction.transaction_status != PaymentStatus.PENDING:
            return Response(
                {"transaction_status": transaction.transaction_status},
                status=status.HTTP_200_OK,
            )

        transaction.transaction_id = response_data.get("transaction_id")
        transaction.save()

        if transaction.order.order_type == OrderType.IN_HOUSE:
            if response_data.get("response_code") in ["100", "481"]:
                if str(transaction.amount) != response_data.get(
                    "amount"
                ) or transaction.currency != response_data.get("currency"):
                    transaction.transaction_status = PaymentStatus.INVALID
                    transaction.save()
                    return Response(
                        {"transaction_status": transaction.transaction_status},
                        status=status.HTTP_200_OK,
                    )
                else:
                    # Post processing for inhouse orders
                    transaction.transaction_status = PaymentStatus.SUCCESSFUL
                    transaction.save()
                    # Send necessary signals
                    transaction.invoice_items.update(paid=True)

                    transaction.user.misc.set_order_in_rating()

                    # Check if everything has been paid off.
                    order: Order = transaction.order
                    if order.invoice.invoice_items.filter(paid=False).exists() is False:
                        # Everything is paid!!
                        order.status = OrderStatusType.COMPLETED
                        order.save()
                        send_all_bill_paid_notification.delay(order_id=order.id)
                    else:
                        print("Invoke single pay notification")
                        send_single_bill_paid_notification.delay(
                            invoice_id=order.invoice.id, user_id=transaction.user_id, transaction_id=transaction.id
                        )
                    return Response(
                        {"transaction_status": transaction.transaction_status},
                        status=status.HTTP_200_OK,
                    )
        else:
            if response_data.get("response_code") in ["111", "481"]:
                if str(transaction.amount) != response_data.get(
                    "amount"
                ) or transaction.currency != response_data.get("currency"):
                    transaction.transaction_status = PaymentStatus.INVALID
                    transaction.save()
                    return Response(
                        {"transaction_status": transaction.transaction_status},
                        status=status.HTTP_200_OK,
                    )
                else:
                    # Post processing for pickup orders
                    transaction.transaction_status = PaymentStatus.AUTHORIZED
                    transaction.save()
                    transaction.invoice_items.update(paid=True)

                    transaction.user.misc.set_order_in_rating()

                    order: Order = transaction.order

                    if order.invoice.invoice_items.filter(paid=False).exists() is False:
                        # Everything is paid!!
                        order.status = OrderStatusType.CHECKOUT
                        order.save()
                        # Collect money
                        transactions = Transaction.objects.filter(
                            order=order, transaction_status=PaymentStatus.AUTHORIZED
                        )
                        for t in transactions:
                            result = capture_transaction(
                                t.pt_transaction_id, amount=t.amount
                            )
                            print(f"Transaction capture result: {result}")
                            t.transaction_status = PaymentStatus.SUCCESSFUL
                            t.save()
                        order.confirmed = True
                        order.save()
                        send_new_order_items_confirmed_notification.delay(
                            order_id=order.id
                        )
                        send_all_bill_paid_notification.delay(order_id=order.id)
                    else:
                        print("Invoke single pay notification")
                        send_single_bill_paid_notification.delay(
                            invoice_id=order.invoice.id, user_id=transaction.user_id, transaction_id= transaction.id
                        )
                    return Response(
                        {"transaction_status": transaction.transaction_status},
                        status=status.HTTP_200_OK,
                    )
        transaction.transaction_status = PaymentStatus.FAILED
        transaction.save()

        return Response(
            {"transaction_status": transaction.transaction_status},
            status=status.HTTP_200_OK,
        )


class TransactionViewSet(
    mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@login_required
def invoice_view(request, order_id: int):
    if request.user.is_superuser is False:
        raise PermissionDenied
    invoice = get_object_or_404(Invoice, order__id=order_id)
    return render(request, "invoice/invoice.html", {"invoice": invoice})
