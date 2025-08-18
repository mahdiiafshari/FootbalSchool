from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSchoolManager
from .models import School
from .serializers import SchoolSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Schools.
    Provides list/retrieve/create/update/destroy.
    Includes custom activate/deactivate actions.
    """
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsSchoolManager]

    def get_queryset(self):
        """
        Managers should only see their own school.
        admins see all schools.
        """
        user = self.request.user
        qs = School.objects.select_related("manager")

        if user.is_superuser:  # allow admin full access
            return qs

        # return only manager school
        if hasattr(user, "manager"):
            return qs.filter(manager=user.manager)

        return qs.none()
