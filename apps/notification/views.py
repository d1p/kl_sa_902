from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Action
from .serializers import ActionSerializer


class ActionViewSet(ReadOnlyModelViewSet):
    """
    Get the notification static list for notifications page.
    """

    serializer_class = ActionSerializer

    def get_queryset(self):
        return Action.objects.filter(user=self.request.user)
