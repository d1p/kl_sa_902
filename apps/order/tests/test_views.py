import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from ..types import OrderType
from ..views import OrderViewSet, OrderInviteViewSet

pytestmark = pytest.mark.django_db


class TOrderFixtures:
    @pytest.fixture
    def customer_group(self):
        return mixer.blend("auth.Group", name="Customer")

    @pytest.fixture
    def restaurant_group(self):
        return mixer.blend("auth.Group", name="Restaurant")

    @pytest.fixture
    def restaurant(self, restaurant_group):
        r = mixer.blend("restaurant.Restaurant", is_public=True)
        r.user.groups.add(restaurant_group)
        return r

    @pytest.fixture
    def customer(self, customer_group):
        r = mixer.blend("customer.Customer")
        r.user.groups.add(customer_group)
        return r

    @pytest.fixture
    def other_customer(self, customer_group):
        r = mixer.blend("customer.Customer")
        r.user.groups.add(customer_group)
        return r

    @pytest.fixture
    def food(self, restaurant):
        return mixer.blend("food.FoodItem", user=restaurant.user)

    @pytest.fixture
    def addon(self, food):
        return mixer.blend("food.FoodAddOn", food=food)

    @pytest.fixture
    def order(self, customer, restaurant):
        order = mixer.blend(
            "order.Order", user=customer.user, restaurant=restaurant.user
        )
        order.order_participants.create(user=customer.user)
        order.refresh_from_db()
        return order


class TestOrder(TOrderFixtures):
    def test_place_pickup_order(self, restaurant, customer):
        factory = APIRequestFactory()
        request = factory.post(
            "/", data={"restaurant": restaurant.user.id, "order_type": OrderType.PICK_UP}
        )
        force_authenticate(request, customer.user)
        response = OrderViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create an order."

    def test_invite_user_into_order(self, customer, other_customer, restaurant, order):
        factory = APIRequestFactory()
        request = factory.post(
            "/", data={
                "invited_users": [other_customer.user.id, 9], "order": order.id}
        )
        force_authenticate(request, customer.user)
        response = OrderInviteViewSet.as_view({"post": "create"})(request)
        response.render()
        print(response.content)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should invite the users"
