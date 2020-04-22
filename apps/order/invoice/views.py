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
from apps.order.invoice.utils import (
    verify_transaction,
    process_new_completed_order_earning,
)
from apps.order.models import Order
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

        transaction.pt_transaction_id = response_data.get("transaction_id")
        transaction.save()

        if response_data.get("response_code") in ["100"]:

            tamount = response_data.get("amount")
            aamount = str(transaction.amount)
            if tamount[-1] == "0":
                tamount = tamount[:-1]
                aamount = str(round(transaction.amount, 2))

            print(f"tamount: {tamount}, aamount: {aamount}")

            if tamount != aamount or transaction.currency != response_data.get(
                "currency"
            ):
                # Lets handle the failing state first.
                transaction.transaction_status = PaymentStatus.INVALID
                transaction.save()
                return Response(
                    {"transaction_status": transaction.transaction_status},
                    status=status.HTTP_200_OK,
                )
            else:
                transaction.transaction_status = PaymentStatus.SUCCESSFUL
                transaction.save()
                # Send necessary signals
                transaction.invoice_items.update(paid=True)
                transaction.refresh_from_db()
                order: Order = transaction.order

                if order.invoice.invoice_items.filter(paid=False).exists() is False:
                    # Everything is paid!!
                    if order.order_type is OrderType.PICK_UP:
                        order.status = OrderStatusType.IN_PROCESS
                        order.confirmed = True
                        order.payment_completed = True
                        order.save()
                    else:
                        order.status = OrderStatusType.COMPLETED
                        order.payment_completed = True
                        order.save()
                        process_new_completed_order_earning(order)

                    send_all_bill_paid_notification.delay(order_id=order.id)

                    for participant in order.order_participants.all():
                        participant.user.misc.set_order_in_rating()

                else:
                    send_single_bill_paid_notification.delay(
                        invoice_id=order.invoice.id,
                        user_id=transaction.user_id,
                        transaction_id=transaction.id,
                    )
                return Response(
                    {"transaction_status": transaction.transaction_status},
                    status=status.HTTP_200_OK,
                )
        else:
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
