from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied as DJPermissionDenied
from django.shortcuts import render, get_object_or_404
from rest_framework import mixins
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.account.types import ProfileType
from .forms import MessageForm
from .models import (
    RestaurantTicket,
    RestaurantMessage,
    PreBackedTicketTopic,
    ReportIssue,
    CustomerTicketTopic,
    CustomerTicket,
)
from .serializers import (
    RestaurantTicketSerializer,
    RestaurantMessageSerializer,
    PreBackedTicketTopicSerializer,
    ReportIssueSerializer,
    CustomerTicketTopicSerializer,
    CustomerTicketSerializer,
)
from .tasks import send_new_ticket_notification, send_message_notification


class PreBackedTicketTopicViewSet(ReadOnlyModelViewSet):
    serializer_class = PreBackedTicketTopicSerializer
    permission_classes = [AllowAny]
    queryset = PreBackedTicketTopic.objects.all()
    page_size = 100


class CustomerTicketTopicViewSet(ReadOnlyModelViewSet):
    serializer_class = CustomerTicketTopicSerializer
    permission_classes = [AllowAny]
    queryset = CustomerTicketTopic.objects.all()
    page_size = 100


class CustomerTicketViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = CustomerTicketSerializer
    lookup_field = "id"

    def get_queryset(self):
        return CustomerTicket.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied

        serializer.save(created_by=self.request.user)
        send_new_ticket_notification.delay()


class ReportIssueViewSet(GenericViewSet, mixins.CreateModelMixin):
    queryset = ReportIssue.objects.all()
    serializer_class = ReportIssueSerializer

    def perform_create(self, serializer):
        if self.request.user.profile_type != ProfileType.CUSTOMER:
            raise PermissionDenied
        serializer.save(created_by=self.request.user)


class RestaurantTicketViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = RestaurantTicketSerializer
    lookup_field = "id"

    def get_queryset(self):
        return RestaurantTicket.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.profile_type != ProfileType.RESTAURANT:
            raise PermissionDenied

        serializer.save(created_by=self.request.user)
        send_new_ticket_notification.delay()


class RestaurantMessageListCreate(ListCreateAPIView):
    serializer_class = RestaurantMessageSerializer
    page_size = 15
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ticket = self.kwargs.get("ticket")
        return RestaurantMessage.objects.filter(
            ticket__id=ticket, ticket__created_by=self.request.user
        )

    def perform_create(self, serializer):
        try:
            ticket_id = self.kwargs.get("ticket")
            ticket = RestaurantTicket.objects.get(id=ticket_id)
        except RestaurantTicket.DoesNotExist:
            raise ValidationError({"ticket": "Invalid ticket"})

        sender = self.request.user
        serializer.save(ticket=ticket, sender=sender)


@login_required()
def admin_chat_thread(request, thread_id: str):
    if request.user.is_superuser is False:
        raise DJPermissionDenied
    ticket = get_object_or_404(RestaurantTicket, id=thread_id)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = ticket.messages.create(
                text=form.cleaned_data.get("text"), sender=request.user
            )
            send_message_notification.delay(message.id)
            ticket.new_message = False
            ticket.save()
            ticket.refresh_from_db()
    return render(
        request, "ticket/thread.html", {"ticket": ticket, "form": MessageForm}
    )
