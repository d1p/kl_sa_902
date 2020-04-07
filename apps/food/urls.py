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

router.register("food/category", FoodCategoryViewSet, basename="food-category")
router.register("food/item", FoodItemViewSet, basename="food-item")
router.register("food/add-on", FoodAddOnViewSet, basename="food-add-on")
router.register("food/attribute", FoodAttributeViewSet, basename="food-attribute")
router.register(
    "food/attribute-matrix",
    FoodAttributeMatrixViewSet,
    basename="food-attribute-matrix",
)


urlpatterns = [path("api/", include(router.urls))]
