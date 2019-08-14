from rest_framework import permissions

from apps.account.types import ProfileType


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    def has_permission(self, request, views):
        if request.user.is_authenticated:
            return True
        else:
            if request.method == "POST":
                return True
            else:
                return False


class IsRestaurantOrViewOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated is False:
            return False
        if request.user.profile_type != ProfileType.RESTAURANT:
            # basically if user is a customer then only allow get method
            if request.method != "GET":
                return False
        return True
