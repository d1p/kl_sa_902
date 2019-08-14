from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet

from apps.account.restaurant.filters import RestaurantTableFilter, RestaurantFilter
from apps.account.restaurant.models import Restaurant, Category, RestaurantTable
from apps.account.restaurant.serializers import (
    CategorySerializer,
    RestaurantSerializer,
    RestaurantTableSerializer,
)
from utils.permission import IsAuthenticatedOrCreateOnly, IsRestaurantOrViewOnly


class RestaurantCategoryViewSet(ReadOnlyModelViewSet):
    """
    Return restaurant categories in ascending order.
    """

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("name")


class RestaurantViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    """
    #### Note
    geolocation = { "latitude": Latitude, "longitude": Longitude }
    """

    permission_classes = [IsAuthenticatedOrCreateOnly]
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    lookup_field = "user"
    filter_backends = [DjangoFilterBackend]
    filterset_class = RestaurantFilter


class RestaurantTableViewSet(ModelViewSet):
    serializer_class = RestaurantTableSerializer
    permission_classes = [IsRestaurantOrViewOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RestaurantTableFilter

    def get_queryset(self):
        return RestaurantTable.objects.filter(is_active=True)

    def perform_create(self, serializer):
        restaurant = self.request.user.restaurant
        serializer.save(restaurant=restaurant)

    def perform_update(self, serializer):
        instance: RestaurantTable = self.get_object()
        if instance.restaurant.user != self.request.user:
            raise PermissionDenied

    def perform_destroy(self, instance):
        instance: RestaurantTable = self.get_object()
        if instance.restaurant.user != self.request.user:
            raise PermissionDenied
