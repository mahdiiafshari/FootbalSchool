from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

def validate_iranian_sheba(value):
    """
    Validator for Sheba number.
    It must start with 'IR' followed by 24 digits.
    """
    pattern = r'^IR\d{24}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'The sheba number must start with IR and the next 24 digits must be a number. Example: IR123456789012345678901234'
        )

class Manager(models.Model):
    """
    Represents a football school manager.

    Each manager is linked to a user account.
    Managers are responsible for creating and managing football schools,
    hiring coaches, managing teams, and overseeing financial operations.
    """

    user = models.OneToOneField(get_user_model(), on_delete=models.PROTECT,related_name='manager')
    bank_account_number = models.CharField(max_length=26,blank=True,null=True,
        validators=[validate_iranian_sheba],
        help_text="The Sheba number must start with 'IR' ")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

    def clean(self):
        # Ensure the linked user has role 'manager'
        if self.user.role != self.user.MANAGER:
            raise ValidationError({'user': 'Selected user does not have the role "manager".'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)