from apps.account.restaurant.models import Restaurant, Category
from apps.account.restaurant.serializers import CategorySerializer, RestaurantSerializer
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from utils.permission import IsAuthenticatedOrCreateOnly


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
):
    """
    #### Note
    geolocation = { "latitude": Latitude, "longitude": Longitude }
    """

    permission_classes = [IsAuthenticatedOrCreateOnly]
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    lookup_field = "user"
