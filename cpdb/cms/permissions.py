from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthenticatedOrReadOnlyOrCreate(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS + ('POST',) or
            request.user and
            request.user.is_authenticated()
        )
