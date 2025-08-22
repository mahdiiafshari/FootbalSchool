# players/views.py
from rest_framework import viewsets, generics
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view

from school.models import School
from .models import Player
from .permissions import IsManagerOrReadOnly
from .serializers import PlayerSerializer


@extend_schema(
    tags=["Players"],
    summary="List players for a given manager",
    description=(
        "Retrieve a list of players belonging to the manager's schools.\n\n"
        "- **Managers**: See only their players.\n"
        "- **Admins**: Can see all players."
    ),
)
class PlayerViewSet(viewsets.ModelViewSet):
    """
    DRF viewset to handle CRUD operations for players with proper permissions.
    """
    serializer_class = PlayerSerializer
    permission_classes = [IsManagerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Player.objects.select_related('user', 'manager', 'school').all()
        if user.role == user.MANAGER:
            return Player.objects.select_related('user', 'manager', 'school').filter(manager__user=user)
        return Player.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != user.MANAGER:
            raise PermissionError("Only managers can create players.")
        manager = get_object_or_404(user.manager.__class__, user=user)  # Ensure manager object exists
        school = get_object_or_404(School, manager=manager)
        serializer.save(manager=manager, school=school)

    def perform_update(self, serializer):
        player = self.get_object()
        if player.manager.user != self.request.user:
            raise PermissionError("You are not authorized to update this player.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.manager.user != self.request.user:
            raise PermissionError("You are not authorized to delete this player.")
        instance.delete()


# ---------------------------
# School-based Player Listing
# ---------------------------
@extend_schema(
    tags=["Players"],
    summary="List players of a school",
    description="Retrieve all players in the manager's school.\n\n- Managers: Only their school.\n- Admins: Can see all schools."
)
class SchoolPlayerListAPIView(generics.ListAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Admin can see all
        if user.is_superuser:
            return Player.objects.select_related('user', 'manager', 'school').all()

        # Manager sees only their school's players
        if user.role == user.MANAGER:
            return Player.objects.select_related('user', 'manager', 'school').filter(manager__user=user)

        return Player.objects.none()
