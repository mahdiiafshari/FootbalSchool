# players/views.py
from rest_framework import viewsets
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
class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Superuser can see all players
        if user.is_superuser:
            return Player.objects.all()
        # If user is a manager , filter by their manager record
        if hasattr(user, "manager"):
            return Player.objects.filter(manager=user.manager)

        return Player.objects.none()


@extend_schema_view(
    list=extend_schema(
        tags=["Players"],
        summary="List players",
        description="Retrieve a list of players.\n\n- Managers: Only see players from their schools.\n- Admins: Can see all players."
    ),
    retrieve=extend_schema(
        tags=["Players"],
        summary="Retrieve player details",
        description="Retrieve details of a single player if you are authorized."
    ),
    create=extend_schema(
        tags=["Players"],
        summary="Create a new player",
        description="Managers can create a new player for their school."
    ),
    update=extend_schema(
        tags=["Players"],
        summary="Update player",
        description="Managers can update players in their school."
    ),
    destroy=extend_schema(
        tags=["Players"],
        summary="Delete player",
        description="Managers can delete players in their school."
    )
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
        if hasattr(user, "manager"):
            return Player.objects.select_related('user', 'manager', 'school').filter(manager=user.manager)
        return Player.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, "manager"):
            raise PermissionError("Only managers can create players.")
        manager = user.manager
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
