from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='account_login'),
    path('signup/', views.CustomSignupView.as_view(), name='account_signup'),
    path('logout/', views.CustomLogoutView.as_view(), name='account_logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('accounts/profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('accounts/profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('account/actions/', views.AccountActionsView.as_view(), name='account_actions'),
    path('confirm-email/', views.CustomEmailVerificationSentView.as_view(), name='account_email_verification_sent'),
    path('confirm-email/<str:key>/', views.CustomConfirmEmailView.as_view(), name='account_confirm_email'),
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='account_change_password'),
    path('password/reset/', views.CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('password/reset/done/', views.CustomPasswordResetDoneView.as_view(), name='account_reset_password_done'),
    path('password/reset/key/<uidb36>/<key>/', views.CustomPasswordResetFromKeyView.as_view(), name='account_reset_password_from_key'),
    path('password/reset/key/done/', views.CustomPasswordResetFromKeyDoneView.as_view(), name='account_reset_password_from_key_done'),

    # Danger Zone
    path('delete-account/', views.AccountDeleteView.as_view(), name='account_delete'),
]
