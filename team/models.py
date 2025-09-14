from django.db import models
from manager.models import Manager
from school.models import School, Semester
from coach.models import Coach
from player.models import Player


class Team(models.Model):
    CARD_TRANSFER = 'card_transfer'
    CASH = 'cash'
    ONLINE = 'online'

    name = models.CharField(max_length=100, verbose_name="Team Name")
    coach = models.ForeignKey('coach.Coach', on_delete=models.CASCADE, verbose_name="Coach", null=True, blank=True,
                              related_name='teams')
    players = models.ManyToManyField('player.Player', blank=True, verbose_name="Players")
    school = models.ForeignKey('school.School', on_delete=models.CASCADE, verbose_name="School", related_name='teams')
    semester = models.ForeignKey('school.Semester', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='teams', verbose_name="Semester")
    manager = models.ForeignKey('manager.Manager', on_delete=models.CASCADE, verbose_name="Manager")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    specialization_field = models.CharField(max_length=150)
    location = models.CharField(max_length=255, verbose_name="General Location", null=True, blank=True)
    team_training_location = models.CharField(max_length=255, verbose_name="Specific Training Location")
    team_capacity = models.PositiveIntegerField(verbose_name="Team Capacity")

    # Scheduling
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    start_time = models.TimeField(verbose_name="Class Start Time")

    class_duration = models.PositiveIntegerField(verbose_name="Class Duration")
    event_days = models.ManyToManyField('EventDay')

    # Equipment
    special_equipment_required = models.BooleanField(default=False, verbose_name="Special Equipment Required")
    special_equipment_description = models.TextField(blank=True, null=True,
                                                     verbose_name="Special Equipment Description")

    payment_type = models.CharField(max_length=50,
                                    choices=[
                                        (CARD_TRANSFER, 'card transfer'),
                                        (CASH, 'cash'),
                                        (ONLINE, 'online'),
                                    ]
                                    )
    price_per_month = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return self.name

    @property
    def get_event_days(self):
        return ', '.join([day.name for day in self.event_days.all()])


class EventDay(models.Model):
    DAY_CHOICES = [
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
    ]
    name = models.CharField(max_length=3, choices=DAY_CHOICES, unique=True)

    class Meta:
        verbose_name = "Event Day"
        verbose_name_plural = "Event Days"
        ordering = ['name']

    def __str__(self):
        return str(self.name)
