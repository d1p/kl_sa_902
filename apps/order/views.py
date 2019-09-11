from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import GenericViewSet

from apps.account.types import ProfileType
from utils.permission import IsCustomer
from .filters import OrderFilter, OrderItemFilter
from .models import OrderInvite, Order, OrderItem, OrderItemInvite
from .serializers import (
    OrderInviteSerializer,
    OrderSerializer,
    OrderItemSerializer,
    OrderItemInviteSerializer,
)


class OrderInviteViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    serializer_class = OrderInviteSerializer
    queryset = OrderInvite.objects.all()
    permission_classes = [IsCustomer]

    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)


class OrderItemInviteViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    serializer_class = OrderItemInviteSerializer
    queryset = OrderItemInvite.objects.all()
    permission_classes = [IsCustomer]

    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = OrderSerializer
    filter_backends = DjangoFilterBackend
    filterset_class = OrderFilter

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
        current_user = self.request
        if current_user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(created_by=current_user)


class OrderItemViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = OrderItemSerializer
    filter_backends = DjangoFilterBackend
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
        current_user = self.request
        if current_user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(added_by=current_user)
