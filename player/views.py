# players/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Player
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
