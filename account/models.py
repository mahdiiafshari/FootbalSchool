import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField


def validate_image_size(value):
    """Validate image file size (max 5MB)"""
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('Image file size cannot exceed 5MB.')


class User(AbstractUser):
    """
    Custom user model with different roles for football school management
    """
    MANAGER = 'manager'
    COACH = 'coach'
    PLAYER = 'player'

    ROLE_CHOICES = [
        (MANAGER, 'Manager'),
        (COACH, 'Coach'),
        (PLAYER, 'Player'),
    ]

    username = models.CharField(
        max_length=25,
        unique=True,
        help_text='Required. 25 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    email = models.EmailField(
        max_length=50,
        unique=True,
        help_text='Required. Enter a valid email address.'
    )
    phone_number = PhoneNumberField(
        unique=True,
        help_text='Required. Enter a valid phone number.'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=PLAYER,
        help_text='User role in the football school system'
    )

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        return f"{self.username}"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def is_manager(self):
        """Check if user is a manager"""
        return self.role == self.MANAGER

    def is_coach(self):
        """Check if user is a coach"""
        return self.role == self.COACH

    def is_player(self):
        """Check if user is a player"""
        return self.role == self.PLAYER


class Profile(models.Model):
    """
    User profile model with QR code generation for football school members
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    image_profile = models.ImageField(
        upload_to='profile/',
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text='Profile image (max 5MB)'
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        help_text='Auto-generated QR code for user identification'
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text='Unique identifier for QR code generation'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def generate_qr_code(self):
        """Generate QR code based on UUID"""
        if not self.qr_code:
            try:
                data = str(self.uuid)
                img = qrcode.make(data)
                buffer = BytesIO()
                img.save(buffer, 'PNG')
                buffer.seek(0)
                filename = f"profile_{self.uuid}.png"

                self.qr_code.save(
                    filename,
                    ContentFile(buffer.read()),
                    save=False
                )
                buffer.close()
            except Exception as e:
                # Log the error if needed
                pass

    def save(self, *args, **kwargs):
        """Save profile and generate QR code if not exists"""
        self.generate_qr_code()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete profile and associated files"""
        if self.image_profile:
            self.image_profile.delete(save=False)
        if self.qr_code:
            self.qr_code.delete(save=False)
        super().delete(*args, **kwargs)
