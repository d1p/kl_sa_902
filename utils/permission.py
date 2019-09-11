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


class IsRestaurantOwnerOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated is False:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.profile_type != ProfileType.RESTAURANT:
            return False

        return obj.user == request.user


class IsCustomer(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.profile_type == ProfileType.CUSTOMER
