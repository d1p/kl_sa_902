from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RestaurantTicketViewSet,
    RestaurantMessageListCreate,
    PreBackedTicketTopicViewSet,
    ReportIssueViewSet,
    CustomerTicketTopicViewSet,
    CustomerTicketViewSet,
    admin_chat_thread,
)

router = DefaultRouter()
router.register(
    "customer-ticket-topics",
    CustomerTicketTopicViewSet,
    basename="customer-ticket-topic",
)
router.register("customer-ticket", CustomerTicketViewSet, basename="ticket")

router.register("restaurant-ticket", RestaurantTicketViewSet, basename="ticket")
router.register("report-issue", ReportIssueViewSet, basename="report-issue")

router.register(
    "restaurant-pre-ticket-topics",
    PreBackedTicketTopicViewSet,
    basename="restaurant-pre-ticket-topic",
)
urlpatterns = [
    path(
        "api/restaurant-ticket-message/<str:ticket>/",
        RestaurantMessageListCreate.as_view(),
        name="restaurant-ticket-message",
    ),
    path(
        "admin/restaurant-ticket/<str:thread_id>/",
        admin_chat_thread,
        name="admin_chat_thread",
    ),
    path("api/", include(router.urls)),
]
