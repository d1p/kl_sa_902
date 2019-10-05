import json

import pytest
from django.contrib.auth.models import Group
from fcm_django.models import FCMDevice
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.order.invoice.views import InvoiceViewSet
from apps.order.tests.test_views import TOrderFixtures

pytestmark = pytest.mark.django_db


class TestInvoice(TOrderFixtures):
    def test_generate_invoice(self, customer, other_customer, food, addon, attribute_matrix, order):
        order.order_participants.create(user=other_customer.user)
        order.refresh_from_db()

        order_item = mixer.blend(
            "order.OrderItem",
            food_item=food,
            quantity=3,
            order=order,
            added_by=customer.user,
            shared_with=[customer.user, other_customer.user],
        )

        factory = APIRequestFactory()
        request = factory.post("/", data={
            "order": order.id,
        })

        force_authenticate(request, customer.user)

        response = InvoiceViewSet.as_view({"post": "create"})(request)
        assert response.status_code == status.HTTP_201_CREATED, "Should create an invoice instance"