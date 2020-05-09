import json

import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from apps.account.customer.models import Customer
from apps.contact.models import ContactGroup
from ..views import ContactListSyncApiView, ContactGroupViewSet

pytestmark = pytest.mark.django_db


class TestSyncContacts:
    @pytest.fixture
    def groups(self):
        return mixer.blend("auth.Group", name="Customer")

    @pytest.fixture
    def customer(self):
        return mixer.blend("customer.Customer")

    def test_sync_contacts(self, groups, customer):
        active_contacts = []
        for i in range(0, 9):
            active_contacts.append(
                mixer.blend("customer.Customer", user__phone_number=f"018763662{i}")
            )
        mixer.cycle(2).blend("customer.Customer")

        for a in active_contacts:
            a.user.groups.add(groups)

        ids = [contact.user.phone_number for contact in active_contacts]
        factory = APIRequestFactory()
        request = factory.post("/", data={"contacts": ids})
        force_authenticate(request, customer.user)

        response = ContactListSyncApiView.as_view()(request)

        assert (
            response.status_code == status.HTTP_200_OK
        ), "Should return http response 200"
        response.render()
        content = json.loads(response.content)
        assert len(content) == 9, "Should return 9 contacts"


class TestGroupViewSet:
    @pytest.fixture
    def groups(self):
        return mixer.blend("auth.Group", name="Customer")

    @pytest.fixture
    def customer(self):
        return mixer.blend("customer.Customer")

    def test_create_a_new_group(self, customer, groups):
        factory = APIRequestFactory()
        request = factory.post("/", data={"name": "Family"})
        force_authenticate(request, customer.user)

        response = ContactGroupViewSet.as_view({"post": "create"})(request)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should Create a new group"

    def test_edit_group(self, customer, groups):
        factory = APIRequestFactory()
        cgroup = mixer.blend("contact.ContactGroup", user=customer.user)
        request = factory.put("/", data={"name": "Family"})
        force_authenticate(request, customer.user)

        response = ContactGroupViewSet.as_view({"put": "update"})(request, id=cgroup.id)
        assert response.status_code == status.HTTP_200_OK, "Should edit the group"

    def test_delete_group(self, customer, groups):
        factory = APIRequestFactory()
        cgroup = mixer.blend("contact.ContactGroup", user=customer.user)
        request = factory.delete("/")
        force_authenticate(request, customer.user)

        response = ContactGroupViewSet.as_view({"delete": "destroy"})(
            request, id=cgroup.id
        )
        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), "Should delete the group"

    def test_cracking_delete_group(self, customer, groups):
        factory = APIRequestFactory()
        cgroup = mixer.blend("contact.ContactGroup", user=customer.user)
        c = mixer.blend("customer.Customer")
        request = factory.delete("/")
        force_authenticate(request, c.user)

        response = ContactGroupViewSet.as_view({"delete": "destroy"})(
            request, id=cgroup.id
        )
        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), "Should not delete the group"

    def test_add_remove_contact_into_group(self, customer, groups):
        factory = APIRequestFactory()

        contact: Customer = mixer.blend("customer.Customer")
        contact.user.groups.add(groups)

        contactGroup: ContactGroup = mixer.blend(
            "contact.ContactGroup", user=customer.user
        )

        request = factory.post("/", data={"ids": [contact.user.id]})

        force_authenticate(request, customer.user)

        response = ContactGroupViewSet.as_view({"post": "contacts"})(
            request, id=contactGroup.id
        )

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Should add the contact into group"

        assert contactGroup.contacts.count() == 1, "Should have a single contact"
