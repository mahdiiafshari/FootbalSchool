from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Manager
from .serializers import ManagerSerializer

@extend_schema_view(
    list=extend_schema(summary="Retrieve all football school managers", tags=["Managers"]),
    retrieve=extend_schema(summary="Retrieve details of a specific manager", tags=["Managers"]),
    create=extend_schema(summary="Add a new football school manager", tags=["Managers"]),
    update=extend_schema(summary="Update manager information", tags=["Managers"]),
    partial_update=extend_schema(summary="Partially update manager information", tags=["Managers"]),
    destroy=extend_schema(summary="Remove a manager from the system", tags=["Managers"]),
)
class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admins can see all managers
        if user.is_staff:
            return self.queryset

        # Managers can only see their own record
        if user.role == user.MANAGER:
            return self.queryset.filter(user=user)

        # Others cannot see anything
        return self.queryset.none()

    def perform_update(self, serializer):
        # Ensure a manager can only update their own record
        user = self.request.user
        if user.role == user.MANAGER and serializer.instance.user != user:
            raise PermissionError("You can only update your own manager record.")
        serializer.save()