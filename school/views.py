from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSchoolManager
from .models import School
from .serializers import SchoolSerializer


@extend_schema(
    tags=["Schools"],
    summary="List schools",
    description=(
        "Retrieve a list of schools.\n\n"
        "- **Admin users**: Can see all schools.\n"
        "- **Managers**: Can only see their own school."
    ),
    responses={200: SchoolSerializer(many=True)},
)
class SchoolViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Schools.
    """
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsSchoolManager]

    def get_queryset(self):
        """
        Managers should only see their own school.
        Admins see all schools.
        """
        user = self.request.user
        qs = School.objects.select_related("manager")

        if user.is_superuser:  # allow admin full access
            return qs

        # return only manager school
        if hasattr(user, "manager"):
            return qs.filter(manager=user.manager)

        return qs.none()

    @extend_schema(
        summary="Retrieve a school",
        description=(
            "Get details of a specific school.\n\n"
            "- **Admin**: Can access any school.\n"
            "- **Manager**: Can only access their own school."
        ),
        responses={
            200: SchoolSerializer,
            403: OpenApiResponse(description="Not allowed to access this school."),
            404: OpenApiResponse(description="School not found."),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a school",
        description=(
            "Create a new school.\n\n"
            "- **Manager**: Can create their own school (manager auto-assigned).\n"
            "- **Admin/Other roles**: Cannot create schools."
        ),
        request=SchoolSerializer,
        responses={
            201: SchoolSerializer,
            403: OpenApiResponse(description="Only managers can create schools."),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update a school",
        description=(
            "Update details of an existing school.\n\n"
            "- **Admin**: Can update any school.\n"
            "- **Manager**: Can only update their own school."
        ),
        request=SchoolSerializer,
        responses={
            200: SchoolSerializer,
            403: OpenApiResponse(description="Not allowed to update this school."),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update a school",
        description=(
            "Partially update school details.\n\n"
            "- **Admin**: Can update any school.\n"
            "- **Manager**: Can only update their own school."
        ),
        request=SchoolSerializer,
        responses={
            200: SchoolSerializer,
            403: OpenApiResponse(description="Not allowed to update this school."),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a school",
        description=(
            "Delete a school.\n\n"
            "- **Admin**: Can delete any school.\n"
            "- **Manager**: Can only delete their own school."
        ),
        responses={
            204: OpenApiResponse(description="School deleted successfully."),
            403: OpenApiResponse(description="Not allowed to delete this school."),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user

        # Only managers can create schools
        if user.role == "manager":
            serializer.save(manager=user.manager)
        else:
            raise PermissionError("Only managers can create schools.")
