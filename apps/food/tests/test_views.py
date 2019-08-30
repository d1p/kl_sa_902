import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.food.views import FoodCategoryViewSet, FoodItemViewSet

pytestmark = pytest.mark.django_db


class TestFoodCategoryViewSet:
    @pytest.fixture
    def groups(self):
        return mixer.blend("auth.Group", name="Restaurant")

    @pytest.fixture
    def restaurant1(self, groups):
        r = mixer.blend("restaurant.Restaurant", is_public=True)
        r.user.groups.add(groups)
        return r

    @pytest.fixture
    def restaurant2(self, groups):
        r = mixer.blend("restaurant.Restaurant", is_public=True)
        r.user.groups.add(groups)
        return r

    def test_add_new_category(self, restaurant1):
        data = {"name": "Burgers"}
        factory = APIRequestFactory()
        request = factory.post("/", data=data)
        force_authenticate(request, restaurant1.user)

        response = FoodCategoryViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create a new category"

    def test_edit_category(self, restaurant1):
        category = mixer.blend("food.FoodCategory", user=restaurant1.user)
        data = {"name": "Burgers"}
        factory = APIRequestFactory()
        request = factory.put("/", data=data)
        force_authenticate(request, restaurant1.user)

        response = FoodCategoryViewSet.as_view({"put": "update"})(
            request, pk=category.id
        )
        assert response.status_code == status.HTTP_200_OK, "Should edit a category"

    def test_delete_category(self, restaurant1):
        category = mixer.blend("food.FoodCategory", user=restaurant1.user)

        factory = APIRequestFactory()
        request = factory.delete("/", data={})
        force_authenticate(request, restaurant1.user)

        response = FoodCategoryViewSet.as_view({"delete": "destroy"})(
            request, pk=category.id
        )
        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), "Should delete a category"

    def test_edit_category_permission(self, restaurant1, restaurant2):
        category = mixer.blend("food.FoodCategory", user=restaurant1.user)

        data = {"name": "Burgers"}
        factory = APIRequestFactory()
        request = factory.put("/", data=data)
        force_authenticate(request, restaurant2.user)

        response = FoodCategoryViewSet.as_view({"put": "update"})(
            request, pk=category.id
        )
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Should not edit a category"

    def test_delete_category_permission(self, restaurant1, restaurant2):
        category = mixer.blend("food.FoodCategory", user=restaurant1.user)

        factory = APIRequestFactory()
        request = factory.delete("/", data={})
        force_authenticate(request, restaurant2.user)

        response = FoodCategoryViewSet.as_view({"delete": "destroy"})(
            request, pk=category.id
        )
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Should not delete a category"


class TestFoodItemViewSet:
    @pytest.fixture
    def groups(self):
        return mixer.blend("auth.Group", name="Restaurant")

    @pytest.fixture
    def restaurant1(self, groups):
        r = mixer.blend("restaurant.Restaurant", is_public=True)
        r.user.groups.add(groups)
        return r

    @pytest.fixture
    def restaurant2(self, groups):
        r = mixer.blend("restaurant.Restaurant", is_public=True)
        r.user.groups.add(groups)
        return r

    @pytest.fixture
    def category(self, restaurant1):
        return mixer.blend("food.FoodCategory", user=restaurant1.user)

    def test_add_new_item(self, restaurant1, category):
        fp = open(os.path.join(os.getcwd(), "test.png"), "rb")
        img = SimpleUploadedFile("test.png", fp.read(), content_type="image/png")

        data = {
            "category": category.id,
            "name": "Burgers",
            "picture": img,
            "price": 99.96,
            "calorie": 854,
            "is_active": True,
        }

        factory = APIRequestFactory()
        request = factory.post("/", data=data)
        force_authenticate(request, restaurant1.user)

        response = FoodItemViewSet.as_view({"post": "create"})(request)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create a new Food item"

    def test_edit_item(self, restaurant1, category):
        item = mixer.blend("food.FoodItem", user=restaurant1.user)
        fp = open(os.path.join(os.getcwd(), "test.png"), "rb")
        img = SimpleUploadedFile("test.png", fp.read(), content_type="image/png")

        data = {
            "category": category.id,
            "name": "Meaw Burger",
            "picture": img,
            "price": 91.96,
            "calorie": 854,
            "is_active": True,
        }

        factory = APIRequestFactory()
        request = factory.put("/", data=data)
        force_authenticate(request, restaurant1.user)

        response = FoodItemViewSet.as_view({"put": "update"})(request, pk=item.id)
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should edit the food item"

    def test_delete_item(self, restaurant1):
        item = mixer.blend("food.FoodItem", user=restaurant1.user)

        factory = APIRequestFactory()
        request = factory.delete("/", data={})
        force_authenticate(request, restaurant1.user)

        response = FoodItemViewSet.as_view({"delete": "destroy"})(request, pk=item.id)
        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), "Should delete a food Item"

    def test_edit_item_permission(self, restaurant1, restaurant2, category):
        item = mixer.blend("food.FoodItem", user=restaurant1.user)
        fp = open(os.path.join(os.getcwd(), "test.png"), "rb")
        img = SimpleUploadedFile("test.png", fp.read(), content_type="image/png")

        data = {
            "category": category.id,
            "name": "Meaw Burger",
            "picture": img,
            "price": 91.96,
            "calorie": 854,
            "is_active": True,
        }

        factory = APIRequestFactory()
        request = factory.put("/", data=data)
        force_authenticate(request, restaurant2.user)

        response = FoodItemViewSet.as_view({"put": "update"})(request, pk=item.id)
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Should not edit the food item"

    def test_delete_item_permission(self, restaurant1, restaurant2):
        item = mixer.blend("food.FoodItem", user=restaurant1.user)

        factory = APIRequestFactory()
        request = factory.delete("/", data={})
        force_authenticate(request, restaurant2.user)

        response = FoodItemViewSet.as_view({"delete": "destroy"})(request, pk=item.id)
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Should not delete a food Item"
