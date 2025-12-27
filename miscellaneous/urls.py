from django.urls import path

from miscellaneous.views import ApiIndexView, HealthView, ErrorLogView

urlpatterns = [
    path("", ApiIndexView.as_view(), name="index"),
    path("health/", HealthView.as_view(), name="health"),
    path("errors/", ErrorLogView.as_view(), name="error_log")
]
