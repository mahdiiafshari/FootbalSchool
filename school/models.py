from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
from manager.models import Manager


class School(models.Model):
    name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(2)],
        verbose_name=_("School Name"),
    )
    address = models.TextField(verbose_name=_("Address"))
    email = models.EmailField(unique=True, verbose_name=_("Official Email"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    manager = models.OneToOneField('manager.Manager', on_delete=models.PROTECT, related_name="school")

    class Meta:
        verbose_name = _("School")
        verbose_name_plural = _("Schools")
        ordering = ["-is_active", "-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def deactivate(self):
        self.is_active = False
        self.save()

class Semester(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    school = models.ForeignKey("school.School", on_delete=models.CASCADE, related_name="semesters")

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.UniqueConstraint(fields=['name', 'school'], name='unique_team_name_per_school')
        ]

    def __str__(self):
        return f"{self.name}"
