import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.account.restaurant.views import RestaurantViewSet


pytestmark = pytest.mark.django_db


class TestCustomerViewSet:
    @pytest.fixture
    def groups(self):
        mixer.blend("auth.Group", name="Restaurant")

    @pytest.fixture
    def restaurant(self):
        return mixer.blend("restaurant.Restaurant", is_public=True)

    def test_registration_success(self, groups):
        data = {
            "user.name": "Pizzaaa",
            "user.phone_number": "+8801978609908",
            "user.email": "zedd@example.com",
            "user.locale": "en",
            "user.password": "zedorbed123",
        }

        factory = APIRequestFactory()

        request = factory.post("/", data=data)
        response = RestaurantViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should register a new restaurant"

    def test_registration_validation_error(self, groups):
        data = {
            "user.name": "Pasta",
            "user.email": "zedd@example.com",
            "user.locale": "en",
            "user.password": "zedorbed123",
        }

        factory = APIRequestFactory()

        request = factory.post("/", data=data)
        response = RestaurantViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Should return validation errors"

    def test_update_profile_success(self, groups, restaurant):
        data = {
            "user.name": "PastaInn",
            "user.email": "zd@example.com",
            "user.locale": "en",
            "online": False,
        }

        factory = APIRequestFactory()

        request = factory.put("/", data=data)
        force_authenticate(request, restaurant.user)
        response = RestaurantViewSet.as_view({"put": "update"})(
            request, user=restaurant.user.id
        )

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should edit restaurants profile"
