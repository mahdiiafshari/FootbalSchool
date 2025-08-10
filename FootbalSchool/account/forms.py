from django.forms import ModelForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Profile
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()


class UserUpdateForm(ModelForm):
    """Form for updating user information"""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
        # Persian error messages for validation feedback
        error_messages = {
            'username': {
                'required': 'نام کاربری الزامی است.',
                'max_length': 'حداکثر طول نام کاربری ۱۵۰ کاراکتر است.',
            },
            'email': {
                'required': 'ایمیل الزامی است.',
                'invalid': 'ایمیل وارد شده معتبر نیست.',
            },
            'phone_number': {
                'required': 'شماره تلفن الزامی است.',
                'invalid': 'شماره تلفن معتبر نیست.',
            },
        }

    def clean_username(self):
        """Validate username uniqueness"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This username has already been used.')
        return username

    def clean_email(self):
        """Validate email uniqueness"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email has already been used.')
        return email

    def clean_phone_number(self):
        """Validate phone number uniqueness"""
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This phone number has already been used.')
        return phone_number


class ProfileUpdateForm(ModelForm):
    """Profile update form (profile image only)"""

    class Meta:
        model = Profile
        fields = ['image_profile']

    def clean_image_profile(self):
        """Validate image file"""
        image = self.cleaned_data.get('image_profile')
        if image:
            # Check file size (5MB limit)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size cannot exceed 5MB.')

            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise ValidationError('Only image files (JPEG, PNG, GIF, WebP) are allowed.')

        return image


class UserCreateForm(UserCreationForm):
    """Form for user registration"""

    phone_number = PhoneNumberField(
        region='IR',
        label='شماره تلفن',
        error_messages={
            'required': 'شماره تلفن الزامی است.',
            'invalid': 'شماره تلفن معتبر نیست.',
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Common CSS classes for form fields
        common_attrs = {
            'class': 'test class',  # this is for future use
        }

        # Apply common attributes to all form fields
        for name, field in self.fields.items():
            if hasattr(field.widget, 'widgets'):
                # For multi-widget fields (like SplitPhoneNumberField)
                for widget in field.widget.widgets:
                    widget.attrs.update(common_attrs)
            else:
                # For simple widgets
                field.widget.attrs.update(common_attrs)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']
        # Persian error messages for registration form
        error_messages = {
            'username': {
                'required': 'نام کاربری الزامی است.',
                'max_length': 'حداکثر طول نام کاربری ۱۵۰ کاراکتر است.',
            },
            'email': {
                'required': 'ایمیل الزامی است.',
                'invalid': 'ایمیل وارد شده معتبر نیست.',
            },
            'phone_number': {
                'required': 'شماره تلفن الزامی است.',
                'invalid': 'شماره تلفن معتبر نیست.',
            },
            'password1': {
                'required': 'لطفاً رمز عبور را وارد کنید.',
            },
            'password2': {
                'required': 'لطفاً تأیید رمز عبور را وارد کنید.',
                'password_mismatch': 'رمزهای عبور وارد شده مطابقت ندارند.',
            },
        }


class UserLoginForm(AuthenticationForm):
    """Form for user login"""

    username = PhoneNumberField(
        region='IR',
        label='شماره تلفن',
        error_messages={
            'required': 'شماره تلفن الزامی است.',
            'invalid': 'شماره تلفن معتبر نیست.',
        },
    )

    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        label='مرا به خاطر بسپار'
    )

    error_messages = {
        'invalid_login': 'شماره تلفن یا رمز اشتباه است.',
        'inactive': 'این حساب غیرفعال است.',
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        # Configure phone number field widget
        phone_widget = self.fields['username'].widget
        phone_widget.attrs.update({
            'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-right',
            'placeholder': '09123456789',
            'autofocus': True,
        })

        # Configure password field widget
        self.fields['password'].widget.attrs.update({
            'placeholder': 'رمز عبور',
            'class': 'w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-right',
        })
