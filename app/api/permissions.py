from rest_framework.permissions import BasePermission
from app.api.models import APIToken


class IsAPITokenAuthenticated(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Token "):
            return False
        
        token_key = auth_header.split(" ")[1]
        try:
            token = APIToken.objects.get(key=token_key)
        except APIToken.DoesNotExist:
            return False
        
        if not token.active:
            return False
        
        return True