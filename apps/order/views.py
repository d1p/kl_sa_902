from rest_framework.generics import CreateAPIView
from .serializers import OrderInviteSerializer
from .models import OrderInvite
from utils.permission import IsCustomer


class OrderInviteAPIView(CreateAPIView):
    serializer_class = OrderInviteSerializer
    queryset = OrderInvite.objects.all()
    permission_classes = [IsCustomer]

    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)
