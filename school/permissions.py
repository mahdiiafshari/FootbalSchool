from rest_framework import permissions

class IsSchoolManager(permissions.BasePermission):
    """
    Allow only the school's assigned manager to update or delete it.
    Read-only access (GET, HEAD, OPTIONS) is allowed for everyone.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS → allow for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if user is the manager of this school
        return hasattr(request.user, "manager") and obj.manager == request.user.manager