from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FoodCategoryViewSet, FoodItemViewSet

router = DefaultRouter()

router.register("food/category", FoodCategoryViewSet, base_name="food-category")
router.register("food/item", FoodItemViewSet, base_name="food-item")
urlpatterns = [path("api/", include(router.urls))]
