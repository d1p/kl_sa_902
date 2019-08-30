import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.food.views import FoodCategoryViewSet

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
