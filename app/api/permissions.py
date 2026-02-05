from rest_framework.permissions import BasePermission


class IsAPITokenAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if not request.authenticators[0].authenticate(request):
            return False

        return True
