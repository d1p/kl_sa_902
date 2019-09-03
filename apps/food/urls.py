from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FoodCategoryViewSet,
    FoodItemViewSet,
    FoodAddOnViewSet,
    FoodAttributeViewSet,
    FoodAttributeMatrixViewSet,
)

router = DefaultRouter()

router.register("food/category", FoodCategoryViewSet, base_name="food-category")
router.register("food/item", FoodItemViewSet, base_name="food-item")
router.register("food/add-on", FoodAddOnViewSet, base_name="food-add-on")
router.register("food/attribute", FoodAttributeViewSet, base_name="food-attribute")
router.register(
    "food/attribute-matrix",
    FoodAttributeMatrixViewSet,
    base_name="food-attribute-matrix",
)


urlpatterns = [path("api/", include(router.urls))]
