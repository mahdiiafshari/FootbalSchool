from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.forms import modelformset_factory

from .forms import AttendanceFormSet, SingleAttendanceForm
from training_session.models import TrainingSession
from manager.models import Manager
from .models import Attendance
from school.models import School
from team.models import Team
from coache.models import Coach
from .mixins import IsManagerOfSchoolMixin, IsCoachOrManagerOfTeamMixin, IsCoachOfTeamMixin, IsUserCoachOfTeamMixin
from players.models import Player



class AttendanceSchoolListView(IsManagerOfSchoolMixin, LoginRequiredMixin, ListView):
    model = Attendance
    template_name = "attendances/attendance_school_list.html"
    context_object_name = "attendances"
    paginate_by = 50

    def get_queryset(self):
        queryset = Attendance.objects.filter(
            training_session__team__school=self.school
        ).select_related("player", "training_session", "training_session__team")

        # filter by team
        team_id = self.request.GET.get("team")
        if team_id:
            queryset = queryset.filter(training_session__team_id=team_id)

        # filter by date
        date = self.request.GET.get("date")
        if date:
            queryset = queryset.filter(training_session__date=date)

        # search by player name or status
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(player__first_name__icontains=query) |
                Q(player__last_name__icontains=query) |
                Q(status__icontains=query)
            )

        return queryset.order_by("-training_session__date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school"] = self.school
        context["teams"] = Team.objects.filter(school=self.school)
        context["query"] = self.request.GET
        return context


class TeamAttendanceListView(IsCoachOrManagerOfTeamMixin, LoginRequiredMixin, ListView):
    model = Attendance
    template_name = "attendances/team_attendance_list.html"
    context_object_name = "attendances"
    paginate_by = 50

    def get_queryset(self):
        team_id = self.kwargs.get("team_id")
        return Attendance.objects.filter(
            training_session__team_id=team_id
        ).select_related("player", "training_session").order_by("-training_session__date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["team"] = get_object_or_404(Team, id=self.kwargs["team_id"])
        return context


# attendances/views.py by ajax
class CoachAttendanceCreateView(LoginRequiredMixin, IsCoachOfTeamMixin, View):
    template_name = "attendances/coach_attendance_form.html"

    def get(self, request, training_session_id):
        session = get_object_or_404(TrainingSession, id=training_session_id)
        team = session.team

        # Check existing attendance records
        existing_attendance = Attendance.objects.filter(training_session=session)

        if existing_attendance.exists():
            formset = AttendanceFormSet(queryset=existing_attendance)
        else:
            # Create initial data for each player
            players = Player.objects.filter(team=team)
            initial_data = [{'player': player} for player in players]
            formset = AttendanceFormSet(queryset=Attendance.objects.none(), initial=initial_data)

        return render(request, self.template_name, {
            'formset': formset,
            'training_session': session,
        })

    def post(self, request, training_session_id):
        session = get_object_or_404(TrainingSession, id=training_session_id)
        formset = AttendanceFormSet(request.POST)

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.training_session = session
                instance.save()
            return redirect('attendances:team-attendance-list')
        return render(request, self.template_name, {
            'formset': formset,
            'training_session': session,
        })


class RecordPlayerAttendanceView(LoginRequiredMixin, IsUserCoachOfTeamMixin, View):
    template_name = 'attendances/record_player_attendance.html'

    def get(self, request, training_session_id, player_id):
        session = get_object_or_404(TrainingSession, id=training_session_id)
        player = get_object_or_404(Player, id=player_id)

        attendance, created = Attendance.objects.get_or_create(
            player=player,
            training_session=session,
        )

        form = SingleAttendanceForm(instance=attendance)

        return render(request, self.template_name, {
            'form': form,
            'player': player,
            'training_session': session,
        })

    def post(self, request, training_session_id, player_id):
        session = get_object_or_404(TrainingSession, id=training_session_id)
        player = get_object_or_404(Player, id=player_id)


        attendance, created = Attendance.objects.get_or_create(
            player=player,
            training_session=session,
        )

        form = SingleAttendanceForm(request.POST, instance=attendance)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.training_session = session
            instance.player = player
            instance.save()
            return redirect('attendances:training_session_player_list', training_session_id=session.id)
        return render(request, self.template_name, {
            'form': form,
            'player': player,
            'training_session': session,
        })

