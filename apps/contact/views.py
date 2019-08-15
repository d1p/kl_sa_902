from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.account.models import User
from apps.contact.models import ContactGroup
from .serializers import (
    ContactListSyncSerializer,
    ContactUserSerializer,
    ContactGroupSerializer,
    IdSerializer,
)


class ContactListSyncApiView(CreateAPIView):
    serializer_class = ContactListSyncSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            contact_list = serializer.validated_data.get("contacts")
            kole_contacts = User.objects.filter(
                groups__name="Customer", phone_number__in=contact_list
            )
            kole_contact_serializer = ContactUserSerializer(kole_contacts, many=True)
            return Response(kole_contact_serializer.data, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactGroupViewSet(ModelViewSet):
    """
    Create contact list groups.
    group name must be unique.
    Add and delete a contact from group.
    response on successfully adding a user into group
    ```{"success": True}``` WITH status HTTP 201
    response on successfully deleting a user from the group
    ```{"success": True}``` WITH status HTTP 204
    response on user not found.
    ```{"id": "User not found."}``` WITH HTTP STATUS 404

    """
    serializer_class = ContactGroupSerializer
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "contacts":
            return IdSerializer
        return ContactGroupSerializer

    def get_queryset(self):
        return ContactGroup.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance: ContactGroup = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["POST", "DELETE"])
    def contacts(self, request, *args, **kwargs):
        group: ContactGroup = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                user = User.objects.get(id=serializer.validated_data.get("id"))
                if user.groups.filter(name="Customer").exists() is False:
                    return Response(
                        {"id": "User not found."}, status=status.HTTP_404_NOT_FOUND
                    )
            except User.DoesNotExist:
                return Response(
                    {"id": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )

            if request.method == "POST":
                if group.contacts.filter(id=user.id).exists() is False:
                    group.contacts.add(user)
                return Response({"success": True}, status.HTTP_201_CREATED)
            else:
                group.contacts.filter(id=user.id).delete()
                return Response({"success": True}, status.HTTP_204_NO_CONTENT)
