from django.urls import path

from auth.views import RegisterView, LoginView, LogoutView, SessionCheckView, GetCSRFTokenView, SendAlertEmailView, \
    AvatarUploadView, MeView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/session/", SessionCheckView.as_view(), name="session"),
    path("auth/csrf/", GetCSRFTokenView.as_view(), name="csrf"),
    path("send-alert-email/", SendAlertEmailView.as_view(), name="send_alert_email"),

    path("profile/upload-avatar/", AvatarUploadView.as_view(), name="upload-avatar"),
    path("profile/me/", MeView.as_view(), name="profile_me"),
]
