from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.account.models import User
from apps.account.types import ProfileType
from apps.order.tasks import send_order_invite_notification
from apps.order.types import OrderInviteStatusType
from utils.permission import IsCustomer
from .filters import OrderFilter, OrderItemFilter
from .models import OrderInvite, Order, OrderItem, OrderItemInvite
from .serializers import (
    OrderInviteSerializer,
    OrderSerializer,
    OrderItemSerializer,
    OrderItemInviteSerializer,
    OrderParticipantSerializer,
    BulkOrderInviteSerializer,
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

    serializer_class = OrderInviteSerializer
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

            if OrderInvite.can_send_invite(invited_by, user, order) is True:
                invite = OrderInvite.objects.create(
                    order=order,
                    invited_user=user,
                    invited_by=invited_by,
                    status=OrderInviteStatusType.PENDING,
                )
                send_order_invite_notification.delay(
                    from_user=invite.invited_by_id,
                    to_user=invite.invited_user_id,
                    invite_id=invite.id,
                )
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)


class OrderItemInviteViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    serializer_class = OrderItemInviteSerializer
    queryset = OrderItemInvite.objects.all()
    permission_classes = [IsCustomer, IsAdminUser]

    def perform_create(self, serializer):
        current_user = self.request
        if current_user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(invited_by=self.request.user)


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

    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
    lookup_field = "pk"

    def get_queryset(self):
        current_user = self.request.user
        if current_user.profile_type == ProfileType.CUSTOMER:
            queryset = Order.objects.filter(
                Q(created_by=current_user)
                | Q(restaurant_order_invites__invited_user__exact=current_user)
            )
        elif current_user.profile_type == ProfileType.RESTAURANT:
            queryset = Order.objects.filter(restaurant=current_user)
        else:
            queryset = Order.objects.all()

        return queryset

    def perform_create(self, serializer):
        current_user = self.request.user
        if current_user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(created_by=current_user)

    @action(detail=True, methods=["GET"])
    def participants(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if order.order_participants.filter(user=request.user).exists() is False:
            return Response(
                {"detail": "You do not have permission to view this."},
                status=status.HTTP_403_FORBIDDEN,
            )

        participants = order.order_participants.all()

        serializer = OrderParticipantSerializer(participants, many=True)
        return Response(serializer.data)


class OrderItemViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderItemFilter

    def get_queryset(self):
        current_user = self.request.user
        if current_user.profile_type == ProfileType.RESTAURANT:
            queryset = OrderItem.objects.filter(order__restaurant=current_user)
        elif current_user.profile_type == ProfileType.CUSTOMER:
            queryset = OrderItem.objects.filter(
                added_by=current_user
            ) | OrderItem.objects.filter(shared_with=current_user)
        else:
            queryset = OrderItem.objects.all()

        return queryset

    def perform_create(self, serializer):
        current_user = self.request.user
        if current_user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(added_by=current_user)
