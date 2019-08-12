import pytest
from mixer.backend.django import mixer
from rest_framework import status
from ..views import TicketViewSet
from rest_framework.test import force_authenticate, APIRequestFactory
import json

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
        factory = APIRequestFactory()

        request = factory.get("/")
        force_authenticate(request, customer.user)
        response = TicketViewSet.as_view({"get": "list"})(request)
        content = json.loads(response.content)
        assert response.status_code == status.HTTP_200_OK, "Should retrieve the list"

        assert content["count"] == 10, "Should have 10 results in total."
