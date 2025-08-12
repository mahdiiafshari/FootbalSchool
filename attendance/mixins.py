from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from team.models import Team
from coach.models import Coach
from manager.models import Manager


class IsCoachOrManagerOfTeamMixin:
    def dispatch(self, request, *args, **kwargs):
        team_id = self.kwargs.get("team_id")
        team = get_object_or_404(
            Team.objects.select_related('school__manager__user', 'coach__user'),
            id=team_id
        )
        user = request.user

        if team.school.manager.user == user or team.coach.user == user:
            return super().dispatch(request, *args, **kwargs)

        return HttpResponseForbidden("Access denied: You are not the coach or manager of this team.")


class IsManagerOfTeamSchoolMixin:
    def dispatch(self, request, *args, **kwargs):
        team_id = self.kwargs.get("team_id")
        team = get_object_or_404(Team.objects.select_related('school__manager'), id=team_id)
        user = request.user

        try:
            manager = Manager.objects.get(user=user)
        except Manager.DoesNotExist:
            return HttpResponseForbidden("Access denied: You are not a manager.")

        if team.school.manager != manager:
            return HttpResponseForbidden("Access denied: You are not the manager of this team’s school.")

        return super().dispatch(request, *args, **kwargs)


class IsManagerOfSchoolMixin:
    def dispatch(self, request, *args, **kwargs):
        school_id = self.kwargs.get("school_id")
        user = request.user

        try:
            manager = Manager.objects.select_related("user").get(user=user)
        except Manager.DoesNotExist:
            return HttpResponseForbidden("Access denied: You are not a manager.")

        school = get_object_or_404(School.objects.select_related("manager"), id=school_id)
        if school.manager != manager:
            return HttpResponseForbidden("Access denied: You are not the manager of this school.")

        self.school = school  # برای استفاده در get_queryset و context
        return super().dispatch(request, *args, **kwargs)


class IsCoachOfTeamMixin:
    def dispatch(self, request, *args, **kwargs):
        team_id = self.kwargs.get("team_id")
        team = get_object_or_404(Team.objects.select_related("coach"), id=team_id)


        try:
            coach = Coach.objects.get(user=request.user)
        except Coach.DoesNotExist:
            return HttpResponseForbidden("Access denied: You are not a coach.")

        if team.coach != coach:
            return HttpResponseForbidden("Access denied: You are not the coach of this team.")

        return super().dispatch(request, *args, **kwargs)


class IsUserCoachOfTeamMixin:
    def dispatch(self, request, *args, **kwargs):
        training_session = get_object_or_404(TrainingSession.objects.select_related('team__coach__user'), id=kwargs.get('training_session_id'))
        if training_session.team.coach.user != request.user:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)
