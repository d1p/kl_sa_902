from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from utils.permission import IsRestaurantOwnerOrReadOnly
from .models import FoodCategory, FoodItem
from .serializers import FoodCategorySerializer, FoodItemSerializer


class FoodCategoryViewSet(ModelViewSet):
    serializer_class = FoodCategorySerializer
    queryset = FoodCategory.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend]
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
    permission_classes = [IsRestaurantOwnerOrReadOnly]
    serializer_class = FoodItemSerializer
    queryset = FoodItem.objects.filter(is_active=True, is_deleted=False)
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance: FoodItem):
        instance.is_deleted = True
        instance.save()
