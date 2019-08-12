from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .models import Ticket
from .serializers import TicketSerializer
from .tasks import send_new_ticket_notification


class TicketViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = TicketSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Ticket.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        send_new_ticket_notification.delay()
