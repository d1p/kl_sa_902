import json

import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from ..models import Ticket
from ..views import TicketViewSet, MessageListCreate

pytestmark = pytest.mark.django_db


class TestTicketViewSet:
    @pytest.fixture
    def groups(self):
        mixer.blend("auth.Group", name="Customer")

    @pytest.fixture
    def customer(self):
        return mixer.blend("customer.Customer")

    def test_create_ticket_success(self, customer):
        factory = APIRequestFactory()
        data = {
            "topic": "Can not order in the application.",
            "description": "Lorem torem insum",
        }
        request = factory.post("/", data=data)
        force_authenticate(request, customer.user)
        response = TicketViewSet.as_view({"post": "create"})(request)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create a new ticket"

    def test_get_ticket_list(self, customer):
        mixer.cycle(10).blend("ticket.Ticket", created_by=customer.user)
        mixer.cycle(5).blend("ticket.Ticket")
        factory = APIRequestFactory()

        request = factory.get("/")
        force_authenticate(request, customer.user)
        response = TicketViewSet.as_view({"get": "list"})(request)
        response.render()
        content = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK, "Should retrieve the list"

        assert content["count"] == 10, "Should have 10 results in total."

    def test_send_message(self, customer):
        ticket = mixer.blend("ticket.Ticket", created_by=customer.user)
        factory = APIRequestFactory()
        request = factory.post("/", data={"text": "lorem ipsum"})
        force_authenticate(request, customer.user)
        response = MessageListCreate.as_view()(request, ticket=ticket.id)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should create a message"

    def test_send_message_in_others_ticket(self, customer):
        ticket = mixer.blend("ticket.Ticket")
        factory = APIRequestFactory()
        request = factory.post("/", data={"text": "lorem ipsum"})
        force_authenticate(request, customer.user)
        response = MessageListCreate.as_view()(request, ticket=ticket.id)
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Should return permission denied error"

    def test_send_message_ticket_closed(self, customer):
        ticket = mixer.blend(
            "ticket.Ticket", status=Ticket.CLOSED, created_by=customer.user
        )
        factory = APIRequestFactory()
        request = factory.post("/", data={"text": "lorem ipsum"})
        force_authenticate(request, customer.user)
        response = MessageListCreate.as_view()(request, ticket=ticket.id)
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Should return validation error"

    def test_send_message_invalid_ticket(self, customer):
        factory = APIRequestFactory()
        request = factory.post("/", data={"text": "lorem ipsum"})
        force_authenticate(request, customer.user)
        response = MessageListCreate.as_view()(request, ticket="8783648723648723asdad")
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Should return validation error"

    def test_receive_text(self, customer):
        ticket = mixer.blend("ticket.Ticket", created_by=customer.user)
        mixer.cycle(10).blend(
            "ticket.Message", ticket=ticket
        )  # Message for original ticket
        mixer.cycle(2).blend("ticket.Message")  # message for others

        factory = APIRequestFactory()
        request = factory.get("/")
        force_authenticate(request, customer.user)
        response = MessageListCreate.as_view()(request, ticket=ticket.id)
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should receive a list of message"

        response.render()
        content = json.loads(response.content)
        assert content["count"] == 10, "Should have 10 results in total."
