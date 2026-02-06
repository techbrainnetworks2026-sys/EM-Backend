from rest_framework.permissions import BasePermission

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Allow Django superuser
        if user.is_superuser:
            return True

        # If you have role field in User model
        return getattr(user, "role", None) == "MANAGER"