from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from manager.models import Manager
from school.models import School


class Coach(models.Model):
    """
    Coach model based on new ERD design.
    Coaches are hired by managers to train teams in schools.
    """

    # Basic Information
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='coach',
        verbose_name=_("User Account")
    )

    # Relationships
    manager = models.ForeignKey(
        'manager.Manager',
        on_delete=models.CASCADE,
        related_name='coaches',
        verbose_name=_("Hiring Manager")
    )

    school = models.ForeignKey(
        'school.School',
        on_delete=models.CASCADE,
        related_name='coaches',
        verbose_name=_("School")
    )

    # Professional Information
    education = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Education Level"),
        help_text=_("Coach's educational background")
    )

    specialty = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Specialty"),
        help_text=_("Coach's main area of expertise (e.g., Goalkeeper, Striker, Defense)")
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Professional Description"),
        help_text=_("Detailed description of coach's experience and skills")
    )

    # Financial Information
    bank_account_number = models.CharField(
        max_length=26,
        blank=True,
        null=True,
        verbose_name=_("Bank Account Number"),
        help_text=_("Coach's bank account for salary payments"),
        validators=[
            RegexValidator(
                regex=r'^IR\d{24}$',
                message=_("Bank account must be in Sheba format (IR + 24 digits)")
            )
        ]
    )

    # Employment Details
    cooperation_start_date = models.CharField(
        blank=True,
        null=True,
        verbose_name=_("Cooperation Start Date"),
        help_text=_("When the coach started working with this school")
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Whether the coach is currently active")
    )

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Coach")
        verbose_name_plural = _("Coaches")
        ordering = ['-cooperation_start_date']
        indexes = [
            models.Index(fields=['cooperation_start_date']),
            models.Index(fields=['school']),
            models.Index(fields=['manager']),
            models.Index(fields=['is_active']),
            models.Index(fields=['specialty']),
        ]

    def __str__(self):

        if self.user and self.user.profile.full_name:
            return f"{self.user.profile.full_name}"
        elif self.user and self.user.username:
            return f"{self.user.username}"
        else:
            return f"{self.school.name}"

    def get_full_name(self):
        """Get coach's full name from profile"""
        if hasattr(self.user, 'profile') and self.user.profile.full_name:
            return self.user.profile.full_name
        return self.user.username if self.user.username else f"Coach {self.id}"

    def get_teams_count(self):
        """Get number of teams coached by this coach"""
        try:
            return self.team_set.count()
        except:
            return 0

    def is_active_coach(self):
        """Check if coach is currently active (has active teams)"""
        try:
            return self.team_set.filter(is_active=True).exists()
        except:
            return False

    # def get_monthly_salary(self):
    #     """Get coach's monthly salary from active contracts"""
    #     try:
    #         from coach_salaries.models import CoachContract
    #         contract = CoachContract.objects.filter(coach=self).first()
    #         return contract.price
    #     except:
    #         return 0

    def get_total_experience_years(self):
        """Calculate total years of experience"""
        # if self.cooperation_start_date:
        #     delta = timezone.now() - self.cooperation_start_date
        #     return delta.days // 365
        return 0


from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender=Coach)
def delete_user_with_coach(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()

