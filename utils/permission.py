from rest_framework import permissions


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    def has_permission(self, request, views):
        if request.user.is_authenticated:
            return True
        else:
            if request.method == "POST":
                return True
            else:
                return False
