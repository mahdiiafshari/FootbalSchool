from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Coach
from .serializers import CoachSerializer
from attendance.models import Attendance
from player.models import Player
from team.models import Team
from django.utils.timezone import now
from datetime import date
from django.db.models import Count, Q
import calendar

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "manager")


class CoachViewSet(viewsets.ModelViewSet):
    queryset = Coach.objects.all()
    serializer_class = CoachSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self):
        return Coach.objects.filter(manager=self.request.user.manager)

    # Equivalent of CoachDashboardView
    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def dashboard(self, request):
        coach = Coach.objects.filter(user=request.user).first()
        if not coach:
            return Response({"detail": "You are not a coach."}, status=status.HTTP_403_FORBIDDEN)

        today = now().date()
        attendance_counts = Attendance.objects.filter(
            player__team__coach=coach,
            recorded_at__date=today
        ).aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="present")),
            absent=Count("id", filter=Q(status="absent"))
        )

        present_percentage = (attendance_counts["present"] / attendance_counts["total"] * 100) if attendance_counts["total"] else 0

        gender_count = Player.objects.filter(team__coach=coach).aggregate(
            total=Count("id"),
            male=Count("id", filter=Q(user__profile__gender="M")),
            female=Count("id", filter=Q(user__profile__gender="F")),
        )

        male_percentage = (gender_count["male"] / gender_count["total"] * 100) if gender_count["total"] else 0
        female_percentage = (gender_count["female"] / gender_count["total"] * 100) if gender_count["total"] else 0

        today = date.today()
        cal = calendar.Calendar(firstweekday=5)
        month_days = list(cal.itermonthdays(today.year, today.month))

        data = {
            "today": today,
            "month_days": month_days,
            "teams_count": Team.objects.filter(coach=coach).count(),
            "players_count": Player.objects.filter(team__coach=coach).count(),
            "attendance_present_count": attendance_counts["present"],
            "attendance_absent_count": attendance_counts["absent"],
            "attendance_present_percentage": round(present_percentage),
            "attendance_absent_percentage": 100 - round(present_percentage),
            "gender_female_percentage": round(female_percentage),
            "gender_male_percentage": round(male_percentage),
            "male_players_count": gender_count["male"],
            "female_players_count": gender_count["female"],
        }
        return Response(data)
