import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.account.customer.views import CustomerViewSet


pytestmark = pytest.mark.django_db


class TestCustomerViewSet:
    @pytest.fixture
    def groups(self):
        mixer.blend("auth.Group", name="Customer")

    @pytest.fixture
    def customer(self):
        return mixer.blend("customer.Customer")

    def test_registration_success(self, groups):
        data = {
            "user.name": "Zedd",
            "user.phone_number": "+88018903786782",
            "user.email": "zedd@example.com",
            "user.locale": "en",
            "user.password": "zedorbed123",
        }

        factory = APIRequestFactory()

        request = factory.post("/", data=data)
        response = CustomerViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should register a new customer"

    def test_update_profile_success(self, groups, customer):
        data = {
            "user.name": "Zedd",
            "user.phone_number": "+88012903786782",
            "user.email": "zd@example.com",
            "user.locale": "en",
        }

        factory = APIRequestFactory()

        request = factory.put("/", data=data)
        force_authenticate(request, customer.user)
        response = CustomerViewSet.as_view({"put": "update"})(
            request, user=customer.user.id
        )

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should edit customers profile"
