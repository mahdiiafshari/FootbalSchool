from django.urls import path
from .views import AttendanceSchoolListView, TeamAttendanceListView, AttendanceCreateView , AttendanceAjaxFormView, CoachAttendanceCreateView, RecordPlayerAttendanceView

app_name = "attendances"

urlpatterns = [
    path("school/<int:school_id>/", AttendanceSchoolListView.as_view(), name="school-attendance-list"),
    path("team/<int:team_id>/", TeamAttendanceListView.as_view(), name="team-attendance-list"),
    path("team/<int:team_id>/session/<int:session_id>/do/", AttendanceCreateView.as_view(), name="attendance_create"),
    path("team/<int:team_id>/session/<int:session_id>/ajax/", AttendanceAjaxFormView.as_view(), name="attendance_ajax_form"),
    path('training-session/<int:training_session_id>/record/', CoachAttendanceCreateView.as_view(), name='attendance_record'),
    path('training-session/<int:training_session_id>/player/<int:player_id>/record/',
        RecordPlayerAttendanceView.as_view(), name='record_player_attendance'),
]
