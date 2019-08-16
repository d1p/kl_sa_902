from django_filters.rest_framework import DjangoFilterBackend

from .serializers import FoodCategorySerializer
from .models import FoodCategory
from rest_framework.viewsets import ModelViewSet


class FoodCategoryViewSet(ModelViewSet):
    serializer_class = FoodCategorySerializer
    queryset = FoodCategory.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend]
