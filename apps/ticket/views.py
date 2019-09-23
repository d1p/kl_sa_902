from rest_framework import mixins
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.account.types import ProfileType
from .models import Ticket, Message, PreBackedTicketTopic, ReportIssue
from .serializers import (
    TicketSerializer,
    MessageSerializer,
    PreBackedTicketTopicSerializer,
    ReportIssueSerializer,
)
from .tasks import send_new_ticket_notification


class PreBackedTicketTopicViewSet(ReadOnlyModelViewSet):
    serializer_class = PreBackedTicketTopicSerializer
    permission_classes = [AllowAny]
    queryset = PreBackedTicketTopic.objects.all()
    page_size = 100


class ReportIssueViewSet(GenericViewSet, mixins.CreateModelMixin):
    queryset = ReportIssue.objects.all()
    serializer_class = ReportIssueSerializer

    def perform_create(self, serializer):
        if self.request.user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(created_by=self.request.user)


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


class MessageListCreate(ListCreateAPIView):
    serializer_class = MessageSerializer
    page_size = 15
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ticket = self.kwargs.get("ticket")
        return Message.objects.filter(
            ticket__id=ticket, ticket__created_by=self.request.user
        )

    def perform_create(self, serializer):
        try:
            ticket_id = self.kwargs.get("ticket")
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            raise ValidationError({"ticket": "Invalid ticket"})

        sender = self.request.user
        serializer.save(ticket=ticket, sender=sender)
