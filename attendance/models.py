from random import choice
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from player.models import Player
from training_session.models import TrainingSession


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", _("Present")
        ABSENT = "absent", _("Absent")
        LATE = "late", _("Late")
        EXCUSED = "excused", _("Excused")

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("Player"),
    )
    training_session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("Training Session"),
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PRESENT,
        verbose_name=_("Attendance Status"),
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Performance Score"),
    )
    trainer_note = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Trainer Note"),
        help_text=_("Optional note or feedback from the trainer."),
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("player", "training_session")
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")
        ordering = ["session__date", "player"]

    def __str__(self):
        return f"{self.player} - {self.training_session} ({self.status})"
