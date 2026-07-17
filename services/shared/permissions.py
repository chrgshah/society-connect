"""Custom REST framework permissions used by service endpoints."""

from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Allow access only to authenticated, active users."""

    def has_permission(self, request, view):
        """Return whether the request user may access the protected view."""
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active
        )
