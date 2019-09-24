from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RestaurantTicketViewSet,
    RestaurantMessageListCreate,
    PreBackedTicketTopicViewSet,
    ReportIssueViewSet,
    CustomerTicketTopicViewSet,
    CustomerTicketViewSet,
)

router = DefaultRouter()
router.register(
    "customer-ticket-topics",
    CustomerTicketTopicViewSet,
    base_name="customer-ticket-topic",
)
router.register("customer-ticket", CustomerTicketViewSet, base_name="ticket")

router.register("restaurant-ticket", RestaurantTicketViewSet, base_name="ticket")
router.register("report-issue", ReportIssueViewSet, base_name="report-issue")

router.register(
    "restaurant-pre-ticket-topics",
    PreBackedTicketTopicViewSet,
    base_name="restaurant-pre-ticket-topic",
)
urlpatterns = [
    path(
        "api/restaurant-ticket-message/<str:ticket>/",
        RestaurantMessageListCreate.as_view(),
        name="restaurant-ticket-message",
    ),
    path("api/", include(router.urls)),
]
