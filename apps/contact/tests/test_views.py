import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from ..views import ContactListSyncApiView
import json

pytestmark = pytest.mark.django_db


class TestSyncContacts:
    @pytest.fixture
    def groups(self):
        return mixer.blend("auth.Group", name="Customer")

    @pytest.fixture
    def customer(self):
        return mixer.blend("customer.Customer")

    def test_sync_contacts(self, groups, customer):
        active_contacts = mixer.cycle(10).blend("customer.Customer")
        inactive_contacts = mixer.cycle(2).blend("customer.Customer")

        for a in active_contacts:
            a.user.groups.add(groups)
        ids = [contact.user.phone_number for contact in active_contacts]
        factory = APIRequestFactory()
        request = factory.post(
            "/", data={"contacts": ids}
        )
        force_authenticate(request, customer.user)

        response = ContactListSyncApiView.as_view()(request)

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return http response 200"
        response.render()
        content = json.loads(response.content)
        assert len(content) == 10, "Should return 10 contacts"
