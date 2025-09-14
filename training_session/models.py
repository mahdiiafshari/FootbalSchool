from django.db import models
from team.models import Team
from coach.models import Coach


class TrainingSession(models.Model):
    team = models.ForeignKey('team.Team', on_delete=models.CASCADE, related_name='training_sessions')
    coach = models.ForeignKey('coach.Coach', on_delete=models.SET_NULL, null=True, blank=True, related_name='training_sessions')
    title = models.CharField(max_length=255)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    session_type = models.CharField(
        max_length=100,
        choices=[
            ('tactical', 'Tactical'),
            ('technical', 'Technical'),
            ('fitness', 'Fitness'),
            ('friendly_match', 'Friendly Match'),
        ],
        default='technical'
    )
    is_canceled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

