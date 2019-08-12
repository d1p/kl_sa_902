from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TicketViewSet, MessageListCreate, PreBackedTicketTopicViewSet

router = DefaultRouter()

router.register("ticket", TicketViewSet, base_name="ticket")
router.register(
    "pre-ticket-topics", PreBackedTicketTopicViewSet, base_name="pre-ticket-topic"
)
urlpatterns = [
    path(
        "api/message/<str:ticket>/", MessageListCreate.as_view(), name="ticket-message"
    ),
    path("api/", include(router.urls)),
]
