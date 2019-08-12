from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TicketViewSet

router = DefaultRouter()

router.register("ticket", TicketViewSet, base_name="ticket")

urlpatterns = [path("api/", include(router.urls))]
