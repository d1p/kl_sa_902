from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from apps.account.types import ProfileType
from utils.permission import IsRestaurantOwnerOrReadOnly
from .filters import (
    FoodItemFilter,
    FoodAddOnFilter,
    FoodAttributeFilter,
    FoodCategoryFilter,
)
from .models import (
    FoodCategory,
    FoodItem,
    FoodAddOn,
    FoodAttributeMatrix,
    FoodAttribute,
)
from .serializers import (
    FoodCategorySerializer,
    FoodItemSerializer,
    FoodAddOnSerializer,
    FoodAttributeSerializer,
    FoodAttributeMatrixSerializer,
)


class FoodCategoryViewSet(ModelViewSet):
    serializer_class = FoodCategorySerializer
    queryset = FoodCategory.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend]
    filterset_class = FoodCategoryFilter
    permission_classes = [IsRestaurantOwnerOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        FoodItem.objects.filter(category=instance).update(is_deleted=True)


class FoodItemViewSet(ModelViewSet):
    """
    The user field is read only, automatically filled from the request context.
    """

    permission_classes = [IsRestaurantOwnerOrReadOnly]
    serializer_class = FoodItemSerializer

    def get_queryset(self):
        user = self.request.user
        if user.profile_type == ProfileType.RESTAURANT:
            return FoodItem.objects.filter(is_deleted=False)
        return FoodItem.objects.filter(
            is_active=True, is_deleted=False, category__is_deleted=False
        )

    filter_backends = [DjangoFilterBackend]
    filterset_class = FoodItemFilter

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance: FoodItem):
        instance.is_deleted = True
        instance.save()


class FoodAddOnViewSet(ModelViewSet):
    serializer_class = FoodAddOnSerializer
    queryset = FoodAddOn.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend]
    filterset_class = FoodAddOnFilter

    def perform_destroy(self, instance: FoodAddOn):
        user = self.request.user
        if instance.food.user != user:
            raise PermissionDenied
        instance.is_deleted = True
        instance.save()


class FoodAttributeViewSet(ModelViewSet):
    serializer_class = FoodAttributeSerializer
    queryset = FoodAttribute.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend]
    filterset_class = FoodAttributeFilter

    def perform_destroy(self, instance: FoodAttribute):
        user = self.request.user
        if instance.food.user != user:
            raise PermissionDenied
        instance.is_deleted = True
        instance.save()


class FoodAttributeMatrixViewSet(ModelViewSet):
    serializer_class = FoodAttributeMatrixSerializer
    queryset = FoodAttributeMatrix.objects.filter(is_deleted=False)

    def perform_destroy(self, instance: FoodAttributeMatrix):
        user = self.request.user
        if instance.attribute.food.user != user:
            raise PermissionDenied
        instance.is_deleted = True
        instance.save()
