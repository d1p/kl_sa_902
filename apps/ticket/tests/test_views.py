import json

import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from ..models import RestaurantTicket
from ..views import (
    RestaurantTicketViewSet,
    RestaurantMessageListCreate,
    CustomerTicketViewSet,
)

pytestmark = pytest.mark.django_db


class TestRestaurantTicketViewSet:
    @pytest.fixture
    def group(self):
        return mixer.blend("auth.Group", name="Restaurant")

    @pytest.fixture
    def restaurant(self, group):
        user = mixer.blend("account.User")
        user.groups.add(group)
        user.save()
        return mixer.blend("restaurant.Restaurant", user=user)

    def test_create_ticket_success(self, restaurant):
        factory = APIRequestFactory()
        data = {
            "topic": "Can not order in the application.",
            "description": "Lorem torem insum",
        }
        request = factory.post("/", data=data)
        force_authenticate(request, restaurant.user)
        response = RestaurantTicketViewSet.as_view({"post": "create"})(request)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create a new ticket"

    def test_get_ticket_list(self, restaurant):
        mixer.cycle(10).blend("ticket.RestaurantTicket", created_by=restaurant.user)
        mixer.cycle(5).blend("ticket.RestaurantTicket")
        factory = APIRequestFactory()

        request = factory.get("/")
        force_authenticate(request, restaurant.user)
        response = RestaurantTicketViewSet.as_view({"get": "list"})(request)
        response.render()
        content = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK, "Should retrieve the list"

        assert content["count"] == 10, "Should have 10 results in total."

    def test_send_message(self, restaurant):
        ticket = mixer.blend("ticket.RestaurantTicket", created_by=restaurant.user)
        factory = APIRequestFactory()
        request = factory.post("/", data={"text": "lorem ipsum"})
        force_authenticate(request, restaurant.user)
        response = RestaurantMessageListCreate.as_view()(request, ticket=ticket.id)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create a message"

    def test_send_message_in_others_ticket(self, restaurant):
        ticket = mixer.blend("ticket.RestaurantTicket")
        factory = APIRequestFactory()
        request = factory.post("/", data={"text": "lorem ipsum"})
        force_authenticate(request, restaurant.user)
        response = RestaurantMessageListCreate.as_view()(request, ticket=ticket.id)
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Should return permission denied error"

    def test_send_message_ticket_closed(self, restaurant):
        ticket = mixer.blend(
            "ticket.RestaurantTicket",
            status=RestaurantTicket.CLOSED,
            created_by=restaurant.user,
        )
        factory = APIRequestFactory()
        request = factory.post("/", data={"text": "lorem ipsum"})
        force_authenticate(request, restaurant.user)
        response = RestaurantMessageListCreate.as_view()(request, ticket=ticket.id)
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Should return validation error"

    def test_send_message_invalid_ticket(self, restaurant):
        factory = APIRequestFactory()
        request = factory.post("/", data={"text": "lorem ipsum"})
        force_authenticate(request, restaurant.user)
        response = RestaurantMessageListCreate.as_view()(
            request, ticket="8783648723648723asdad"
        )
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Should return validation error"

    def test_receive_text(self, restaurant):
        ticket = mixer.blend("ticket.RestaurantTicket", created_by=restaurant.user)
        mixer.cycle(10).blend(
            "ticket.RestaurantMessage", ticket=ticket
        )  # Message for original ticket
        mixer.cycle(2).blend("ticket.RestaurantMessage")  # message for others

        factory = APIRequestFactory()
        request = factory.get("/")
        force_authenticate(request, restaurant.user)
        response = RestaurantMessageListCreate.as_view()(request, ticket=ticket.id)
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should receive a list of message"

        response.render()
        content = json.loads(response.content)
        assert content["count"] == 10, "Should have 10 results in total."


class TestCustomerTicketViewSet:
    @pytest.fixture
    def group(self):
        return mixer.blend("auth.Group", name="Customer")

    @pytest.fixture
    def customer(self, group):
        user = mixer.blend("account.User")
        user.groups.add(group)
        user.save()
        return mixer.blend("customer.Customer", user=user)

    @pytest.fixture
    def topic(self):
        return mixer.blend("ticket.CustomerTicketTopic")

    def test_create_ticket_success(self, customer, topic):
        factory = APIRequestFactory()
        data = {
            "topic": topic.id,
            "sub_topic": "something",
            "description": "Lorem torem insum",
        }
        request = factory.post("/", data=data)
        force_authenticate(request, customer.user)
        response = CustomerTicketViewSet.as_view({"post": "create"})(request)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create a new ticket"
