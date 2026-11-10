from rest_framework.permissions import BasePermission


class IsAPITokenAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.authenticators[0].authenticate(request)
