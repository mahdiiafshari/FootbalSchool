from rest_framework.permissions import IsAuthenticated


class IsManagerOrReadOnly(IsAuthenticated):
    """
    Only managers can create/update/delete players, others can read if allowed.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return hasattr(request.user, "manager") and obj.manager.user == request.user