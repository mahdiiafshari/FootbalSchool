from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class MedicalRecord(models.Model):
    """Medical records for football players based on database diagram"""

    # Foreign keys
    player = models.ForeignKey(
        'player.Player',
        on_delete=models.CASCADE,
        related_name='medical_records',
        verbose_name="Player",
        related_query_name='medical_record'
    )
    training_session = models.ForeignKey(
        'training_session.TrainingSession',
        on_delete=models.CASCADE,
        related_name='medical_records',
        verbose_name="Training Session",
    )

    # Main fields
    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(verbose_name="Description")

    # Dates
    diagnosed_date = models.DateField(verbose_name="Diagnosed Date")
    recovery_date = models.DateField(null=True, blank=True, verbose_name="Recovery Date")

    def clean(self):
        if self.recovery_date and self.diagnosed_date and self.recovery_date < self.diagnosed_date:
            raise ValidationError("Recovery date cannot be earlier than diagnosed date.")

    # Professional notes and details
    psychologist_note = models.CharField(max_length=500, blank=True, verbose_name="Psychologist Note")
    doctor_name = models.CharField(max_length=100, verbose_name="Doctor Name")

    # Status
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_medical_records',
        verbose_name="Created By"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Medical Record"
        verbose_name_plural = "Medical Records"
        ordering = ['-created_at']
        db_table = 'medical_records'

    def __str__(self):
        try:
            if self.player and getattr(self.player, 'user', None):
                username = getattr(self.player.user, 'username', None)
                player_name = username or 'Unknown Player'
            else:
                player_name = 'Unknown Player'
            return f"{player_name} - {self.title}"
        except AttributeError:
            return f"Unknown Player - {self.title}"

    def get_player_name(self):
        """Get the player's full name for display purposes"""
        try:
            if self.player and getattr(self.player, 'user', None):
                username = getattr(self.player.user, 'username', None)
                return username or 'Unknown Player'
            return 'Unknown Player'
        except AttributeError:
            return 'Unknown Player'
