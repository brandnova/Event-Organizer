from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView, UpdateView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.contrib import messages
from allauth.account.views import LoginView, SignupView, LogoutView,PasswordResetView, PasswordChangeView, EmailVerificationSentView, ConfirmEmailView, PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView, PasswordResetFromKeyDoneView
from .forms import CustomLoginForm, CustomSignupForm, CustomResetPasswordForm, ProfileUpdateForm

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/profile.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data you need
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'accounts/profile_edit.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('dashboard')
    
    def get_object(self):
        return self.request.user
    
class AccountActionsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/account_actions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('index')

class CustomSignupView(SignupView):
    template_name = 'accounts/signup.html'
    form_class = CustomSignupForm
    success_url = reverse_lazy('account_login')

class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html'

class CustomEmailVerificationSentView(EmailVerificationSentView):
    template_name = 'accounts/verification_sent.html'

class CustomConfirmEmailView(ConfirmEmailView):
    template_name = 'accounts/email_confirm.html'

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('dashboard')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    form_class = CustomResetPasswordForm

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetFromKeyView(PasswordResetFromKeyView):
    template_name = 'accounts/password_reset_from_key.html'

class CustomPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    template_name = 'accounts/password_reset_from_key_done.html'

class AccountDeleteView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/account_delete.html'

    def post(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('index')