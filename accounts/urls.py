from django.urls import path
from .views import ApprovedUsersView, CurrentUserView, RegisterView, CustomAuthToken, PendingUsersView, ApproveUserView, ForgotPasswordView, VerifyOTPView, ResetPasswordView, ProfileUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('manager/pending-users/', PendingUsersView.as_view(), name='pending_users'),
    path('manager/approve-user/<int:pk>/', ApproveUserView.as_view(), name='approve_user'),
    path('manager/approved-users/', ApprovedUsersView.as_view(), name='approved_users'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
