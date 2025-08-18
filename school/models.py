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
    manager = models.OneToOneField(Manager, on_delete=models.PROTECT, related_name="school")

    class Meta:
        verbose_name = _("School")
        verbose_name_plural = _("Schools")
        ordering = ["-is_active", "-created_at"]
        indexes = [
            models.Index(fields=["manager"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name

    def deactivate(self):
        if self.is_active:
            self.is_active = False
            self.save()
        else:
            raise PermissionError("This school already deactivated.")

    def activate(self):
        if not self.is_active:
            self.is_active = True
            self.save()
        else:
            raise PermissionError("This school already activated.")
