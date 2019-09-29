import json

import pytest
from django.contrib.auth.models import Group
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.account.customer.models import Customer
from apps.account.restaurant.models import Restaurant
from apps.food.models import FoodAddOn, FoodItem, FoodAttributeMatrix
from apps.order.models import Order
from ..types import OrderType, OrderStatusType
from ..views import OrderViewSet, OrderInviteViewSet, OrderItemViewSet

pytestmark = pytest.mark.django_db


class TOrderFixtures:
    @pytest.fixture
    def customer_group(self) -> Group:
        return mixer.blend("auth.Group", name="Customer")

    @pytest.fixture
    def restaurant_group(self) -> Group:
        return mixer.blend("auth.Group", name="Restaurant")

    @pytest.fixture
    def restaurant(self, restaurant_group) -> Restaurant:
        r = mixer.blend("restaurant.Restaurant", is_public=True)
        r.user.groups.add(restaurant_group)
        return r

    @pytest.fixture
    def customer(self, customer_group) -> Customer:
        r = mixer.blend("customer.Customer")
        r.user.groups.add(customer_group)
        mixer.blend("customer.Misc", user=r.user)
        return r

    @pytest.fixture
    def other_customer(self, customer_group) -> Customer:
        r = mixer.blend("customer.Customer")
        r.user.groups.add(customer_group)
        mixer.blend("customer.Misc", user=r.user)
        return r

    @pytest.fixture
    def food(self, restaurant) -> FoodItem:
        return mixer.blend("food.FoodItem", user=restaurant.user)

    @pytest.fixture
    def addon(self, food) -> FoodAddOn:
        return mixer.blend("food.FoodAddOn", food=food)

    @pytest.fixture
    def attribute_matrix(self, food) -> FoodAttributeMatrix:
        attribute = mixer.blend("food.FoodAttribute", food=food)
        return mixer.blend("food.FoodAttributeMatrix", attribute=attribute)

    @pytest.fixture
    def order(self, customer, restaurant) -> Order:
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
            "/",
            data={"restaurant": restaurant.user.id, "order_type": OrderType.PICK_UP},
        )
        force_authenticate(request, customer.user)
        response = OrderViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create an order."

    def test_invite_user_into_order(self, customer, other_customer, restaurant, order):
        factory = APIRequestFactory()
        request = factory.post(
            "/", data={"invited_users": [other_customer.user.id, 9], "order": order.id}
        )
        force_authenticate(request, customer.user)
        response = OrderInviteViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should invite the users"

    def test_add_item_in_order(
        self, customer, restaurant, order, food, addon, attribute_matrix
    ):
        factory = APIRequestFactory()
        data = {
            "order": order.id,
            "food_item": food.id,
            "quantity": 1,
            "order_item_add_ons": [
                dict(food_add_on=addon.id),
                dict(food_add_on=addon.id),
            ],
            "order_item_attribute_matrices": [
                dict(food_attribute_matrix=attribute_matrix.id),
                dict(food_attribute_matrix=attribute_matrix.id),
            ],
        }
        request = factory.post("/", json.dumps(data), content_type="application/json")
        force_authenticate(request, customer.user)
        response = OrderItemViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should add item in the order"

    def test_leave_order(self, customer, order, other_customer):
        factory = APIRequestFactory()
        request = factory.delete("/", data={"sure": True})
        force_authenticate(request, customer.user)
        response = OrderViewSet.as_view({"delete": "leave"})(request, pk=order.id)
        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), "Should remove the user from order."
        order.refresh_from_db()
        assert (
            order.order_participants.all().count() == 0
        ), "Should have zero participant"
        assert order.status == OrderStatusType.CANCELED, "Order should be cancelled."
