from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.order.models import Order
from .models import Action
from .serializers import ActionSerializer, OrderRemainingTimeNotificationSerializer


class ActionViewSet(ReadOnlyModelViewSet):
    """
    Get the notification static list for notifications page.
    """

    serializer_class = ActionSerializer

    def get_queryset(self):
        return Action.objects.filter(user=self.request.user)


class OrderRemainingTimeNotificationView(CreateAPIView):
    serializer_class = OrderRemainingTimeNotificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(id=serializer.validated_data.get("order_id"))
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if order.restaurant != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        for participant in order.order_participants.all():
            pass

        # FoodItem.objects.filter(name="Burger").select_related(:)
