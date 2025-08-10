from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm, UserCreateForm, UserLoginForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


class ProfileDisplayView(LoginRequiredMixin, View):
    """Display user profile (read-only)"""

    template_name = 'account/profile_display.html'

    def get(self, request):
        """Display user profile information"""
        try:
            # Get or 404 profile
            profile = get_object_or_404(Profile.objects.select_related('user'), user=request.user)
            context = {
                'profile': profile,
            }
            return render(request, self.template_name, context)

        except Exception as e:
            messages.error(request, 'Error displaying profile.')
            return redirect('core:home')


class ProfileEditView(LoginRequiredMixin, View):
    """Edit user profile"""

    template_name = 'account/profile_edit.html'

    def get(self, request):
        """Display profile edit form"""
        try:
            # Get or 404 profile
            profile = get_object_or_404(Profile.objects.select_related('user'), user=request.user)

            user_update_form = UserUpdateForm(instance=request.user)
            profile_update_form = ProfileUpdateForm(instance=profile)

            context = {
                'user_update_form': user_update_form,
                'profile_update_form': profile_update_form,
            }
            return render(request, self.template_name, context)
        except Exception as e:
            messages.error(request, 'Error displaying profile.')
            return redirect('account:profile_display')

    def post(self, request):
        """Process profile edit form"""
        try:
            # Get profile
            profile = get_object_or_404(Profile.objects.select_related('user'), user=request.user)

            # Process edit forms
            user_update_form = UserUpdateForm(request.POST, instance=request.user)
            profile_update_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

            # Validate forms
            if user_update_form.is_valid() and profile_update_form.is_valid():
                try:
                    # Save user information
                    user_update_form.save()

                    # Save profile information
                    profile_update_form.save()

                    messages.success(request, 'Your profile has been updated successfully.')
                    return redirect('account:profile_display')

                except ValidationError as e:
                    messages.error(request, f'Validation error: {str(e)}')

                except Exception as e:
                    messages.error(request, 'Error saving information. Please try again.')
            else:
                # Display form errors
                for form_name, form in [('user', user_update_form), ('profile', profile_update_form)]:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'{form_name}.{field}: {error}')

            # Return form with errors
            context = {
                'user_form': user_update_form,
                'profile_form': profile_update_form,
                'profile': profile,
            }

            return render(request, self.template_name, context)

        except Profile.DoesNotExist:  # type: ignore
            messages.error(request, 'Your profile was not found. Please contact support.')
            return redirect('account:profile_display')

        except Exception as e:
            messages.error(request, 'Error processing request. Please try again.')
            return redirect('account:profile_display')


class UserSignupView(View):
    """User registration view"""

    template_name = 'account/signup.html'
    form_class = UserCreateForm
    success_url = 'account:profile_display'

    def get(self, request):
        """Display signup form"""
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Process signup form"""
        form = self.form_class(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class UserLoginView(View):
    """User login view"""

    template_name = 'account/login.html'
    form_class = UserLoginForm
    success_url = 'account:profile_display'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account:profile_display')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """Display login form"""
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Process login form"""
        form = self.form_class(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)

            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form})


class PasswordChangeUserView(LoginRequiredMixin, View):
    """Allow logged-in users to change their password"""

    template_name = 'account/password_change.html'
    form_class = PasswordChangeForm
    success_url = 'account:profile_display'

    def get(self, request):
        """Display password change form"""
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Process password change form"""
        form = self.form_class(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'رمز عبور شما با موفقیت تغییر کرد.')
            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form})


class PasswordResetUserView(View):
    """Allow logged-in users to reset their password"""

    def get(self, request):
        pass
    # this feature is not implemented yet
