from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.account.models import User
from apps.account.types import ProfileType
from apps.order.invoice.models import InvoiceItem, Transaction
from apps.order.tasks import (
    send_order_invite_notification,
    send_order_left_push_notification,
    send_order_item_removed_notification,
    send_new_order_items_confirmed_notification,
    send_update_order_items_confirmed_notification,
    send_update_order_items_confirmed_customer_notification,
    send_order_will_be_ready_in_x_notification,
    send_order_is_ready_notification,
    send_order_is_delivered_notification,
    send_order_rejected_notification,
    send_order_accepted_notification,
)
from apps.order.types import (
    OrderInviteStatusType,
    OrderStatusType,
    OrderItemStatusType,
    OrderType,
)
from .filters import OrderFilter, OrderItemFilter, OrderParticipantFilter
from .invoice.types import PaymentStatus
from .invoice.utils import capture_transaction, process_new_completed_order_earning
from .models import (
    OrderInvite,
    Order,
    OrderItem,
    OrderItemInvite,
    OrderParticipant,
    Rating,
)
from .serializers import (
    OrderInviteSerializer,
    OrderSerializer,
    OrderItemSerializer,
    OrderItemInviteSerializer,
    BulkOrderInviteSerializer,
    BulkOrderItemInviteSerializer,
    ConfirmSerializer,
    OrderParticipantSerializer,
    OrderRatingSerializer,
    OrderIsReadySerializer,
)


class OrderInviteViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    """
    Returns HTTP 201 on successful invites. Upon validation errors it returns normal drf field errors.
    Custom Errors:
    Upon exceeding maximum invite request limit to a individual user it will return validation error with this message.
    ```json
    {"non_field_errors": ["Maximum number of invite exceeded."]}
    ```
    """

    def get_serializer_class(self):
        if self.action == "create":
            return BulkOrderInviteSerializer
        else:
            return OrderInviteSerializer

    queryset = OrderInvite.objects.all()

    def create(self, request, *args, **kwargs):
        invited_by = self.request.user
        if invited_by.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        invited_users = validated_data.get("invited_users")

        try:
            order = Order.objects.get(id=validated_data.get("order"))
        except Order.DoesNotExist:
            return Response(
                {"order": "Invalid Order id"}, status=status.HTTP_400_BAD_REQUEST
            )
        if order.order_participants.filter(user=invited_by).exists() is False:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        for i_user in invited_users:
            try:
                user = User.objects.get(id=i_user)
                if user.profile_type != ProfileType.CUSTOMER:
                    continue
            except User.DoesNotExist:
                continue
            invite = OrderInvite.objects.create(
                order=order,
                invited_user=user,
                invited_by=invited_by,
                status=OrderInviteStatusType.PENDING,
            )
            send_order_invite_notification.delay(
                from_user=invite.invited_by.id,
                to_user=invite.invited_user.id,
                invite_id=invite.id,
            )
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)


class OrderItemInviteViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    def get_serializer_class(self):
        if self.action == "create":
            return BulkOrderItemInviteSerializer
        return OrderItemInviteSerializer

    queryset = OrderItemInvite.objects.all()

    def create(self, request, *args, **kwargs):
        invited_by = self.request.user
        if invited_by.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        invited_users = validated_data.get("invited_users")

        try:
            order_item = OrderItem.objects.get(id=validated_data.get("order_item"))
        except Order.DoesNotExist:
            return Response(
                {"order_item": "Invalid Order Item id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for i_user in invited_users:
            try:
                user = User.objects.get(id=i_user)
                if user.profile_type != ProfileType.CUSTOMER:
                    continue
            except User.DoesNotExist:
                continue
            if (
                OrderItemInvite.can_send_invite(
                    to_user=user, order_item=validated_data.get("order_item")
                )
                is True
            ):
                OrderItemInvite.objects.create(
                    to_user=user,
                    order_item=order_item,
                    invited_by=self.request.user,
                    status=0,
                )

        return Response({"status": "success"}, status=status.HTTP_201_CREATED)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    Use `participants` to get participants of an order.
    it will return an array of public user information.
    such as Name, Profile Picture, ID
    """

    def get_serializer_class(self):
        if self.action in [
            "leave",
            "send_order_is_ready_notification",
            "send_order_is_delivered_notification",
            "accept_order",
        ]:
            return ConfirmSerializer
        elif self.action == "send_order_is_ready_in_x_notification":
            return OrderIsReadySerializer
        return OrderSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    lookup_field = "pk"

    def get_queryset(self):
        current_user = self.request.user
        if current_user.profile_type == ProfileType.CUSTOMER:
            queryset = Order.objects.filter(
                order_participants__user=current_user
            ).distinct("id")
        elif current_user.profile_type == ProfileType.RESTAURANT:
            queryset = (
                Order.objects.filter(restaurant=current_user, confirmed=True)
                .exclude(status=OrderStatusType.CANCELED)
                .exclude(status=OrderStatusType.COMPLETED)
            )
        else:
            queryset = Order.objects.all()

        return queryset

    def perform_create(self, serializer):
        current_user = self.request.user
        if current_user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(created_by=current_user)

    @action(detail=True, methods=["delete"])
    def leave(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = self.get_object()

        if (
            order.order_participants.filter(user=request.user).exists() is True
            and order.confirmed is False
        ):
            OrderParticipant.objects.filter(order=order, user=request.user).delete()

            request.user.misc.set_no_order()

            if order.order_participants.all().count() == 0:
                order.status = OrderStatusType.CANCELED
                order.save()
            send_order_left_push_notification.delay(
                order_id=order.id, from_user=request.user.id
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "failed"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["POST"])
    def confirm_current_items(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("sure") is False:
            return Response({"status": "failed"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        order: Order = self.get_object()

        order_items = order.order_item_set.filter(
            status=OrderItemStatusType.UNCONFIRMED
        )
        if order_items.count() > 0:
            order_items.update(status=OrderItemStatusType.CONFIRMED)
            send_update_order_items_confirmed_customer_notification.delay(
                from_user=request.user.id, order_id=order.id
            )
            if order.order_type == OrderType.PICK_UP:
                if order.confirmed is True:
                    return Response(
                        {"success": True, "message": "Please pay the bill."},
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response(
                        {"success": True, "message": "Please pay the bill."},
                        status=status.HTTP_201_CREATED,
                    )
            else:
                if order.confirmed is False:
                    # Change status and send notification to the restaurant
                    order.confirmed = True
                    order.save()
                    send_new_order_items_confirmed_notification.delay(order_id=order.id)
                else:
                    send_update_order_items_confirmed_notification.delay(
                        order_id=order.id
                    )
                return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"status": "failed", "message": "No new item to confirm in the order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["POST"])
    def send_order_is_ready_in_x_notification(self, request, pk):
        order: Order = self.get_object()
        if order.restaurant != request.user:
            raise PermissionDenied
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_order_will_be_ready_in_x_notification.delay(
            order_id=order.id, time=serializer.validated_data.get("time")
        )
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def send_order_is_ready_notification(self, request, pk):
        order: Order = self.get_object()
        if order.restaurant != request.user:
            raise PermissionDenied
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_order_is_ready_notification.delay(order_id=order.id)
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def send_order_is_delivered_notification(self, request, pk):
        order: Order = self.get_object()
        if order.restaurant != request.user:
            raise PermissionDenied
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_order_is_delivered_notification.delay(order_id=order.id)
        if order.order_type == OrderType.PICK_UP:
            order.status = OrderStatusType.COMPLETED
            order.save()
            process_new_completed_order_earning(order)

        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["POST"])
    def accept_order(self, request, pk):
        order: Order = self.get_object()
        if order.restaurant != request.user:
            raise PermissionDenied
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if order.order_type == OrderType.PICK_UP:
            if order.has_restaurant_accepted is False:
                if serializer.validated_data.get("sure") is True:

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
                    order.has_restaurant_accepted = True
                    order.save()
                    send_order_accepted_notification.delay(order_id=order.id)
                else:
                    order.status = OrderStatusType.CANCELED
                    for participant in order.order_participants.all():
                        participant.user.misc.set_no_order()
                    order.save()
                    send_order_rejected_notification.delay(order_id=order.id)

        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["GET"])
    def payment_info(self, request, pk):
        """
        returning data type example:
        ```json
        [
            {
                    "user": {
                        "id": 123,
                        "name": "john Smith",
                        "profile_picture": "https://example.com/user.jpg,
                    },
                    "amount": 34.345,
                    "has_paid": true
            }
        ]
        ```
        """
        order: Order = self.get_object()
        if order.restaurant != request.user:
            raise PermissionDenied
        response = []
        participants = order.order_participants.all()
        for participant in participants:
            ordered_items = OrderItem.objects.filter(
                order=order,
                shared_with=participant.user,
                status=OrderItemStatusType.CONFIRMED,
            )
            if ordered_items.count() > 0:
                has_paid = False
                if order.status in [
                    OrderStatusType.CHECKOUT,
                    OrderStatusType.COMPLETED,
                ]:
                    try:
                        invoice_item = InvoiceItem.objects.get(
                            order=order, user=participant.user
                        )
                        has_paid = invoice_item.paid
                    except InvoiceItem.DoesNotExist:
                        has_paid = False

                response.append(
                    {
                        "user": {
                            "id": participant.user.id,
                            "name": participant.user.name,
                            "profile_picture": participant.user.profile_picture.url
                            if participant.user.profile_picture
                            else None,
                        },
                        "amount": order.shared_price_with_tax(participant.user),
                        "has_paid": has_paid,
                    }
                )
        return Response(response, status=status.HTTP_200_OK)


class OrderItemViewSet(ModelViewSet):
    """
    delete: Response examples {"status": "failed"}, status=status.HTTP_403_FORBIDDEN on invalid participant trying to
    delete order. {"status": "failed", "message": "Food item is already processing."},
    status=status.HTTP_400_BAD_REQUEST on food item that has already been confirmed order_item.delete() return
    {"status": "success"}, status=status.HTTP_204_NO_CONTENT, On successfully deleting the food item from order
    update:
    Add every addons, matrices with the request.
    """

    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderItemFilter

    def get_queryset(self):
        current_user = self.request.user
        if current_user.profile_type == ProfileType.RESTAURANT:
            queryset = OrderItem.objects.filter(order__restaurant=current_user)
        elif current_user.profile_type == ProfileType.CUSTOMER:
            queryset = OrderItem.objects.filter(
                order__order_participants__user=current_user
            )
        else:
            queryset = OrderItem.objects.all()

        return queryset

    def perform_create(self, serializer):
        current_user = self.request.user
        if current_user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(added_by=current_user)

    def perform_update(self, serializer):
        current_user = self.request.user
        if current_user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        user = request.user
        order_item: OrderItem = self.get_object()
        order_id = order_item.order.id

        if order_item.order.order_participants.filter(user=user).exists() is False:
            return Response({"status": "failed"}, status=status.HTTP_403_FORBIDDEN)
        if order_item.status == OrderItemStatusType.CONFIRMED:
            return Response(
                {"status": "failed", "message": "Food item is already processing."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order_item.delete()
        send_order_item_removed_notification.delay(
            from_user=user.id, order_id=order_id, order_item_id=order_item.id
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderParticipantViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = OrderParticipantSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderParticipantFilter

    def get_queryset(self):
        order = Order.objects.filter(order_participants__user=self.request.user)
        return OrderParticipant.objects.filter(order__in=order)


class OrderRatingViewSet(GenericViewSet, mixins.CreateModelMixin):
    serializer_class = OrderRatingSerializer
    queryset = Rating.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
