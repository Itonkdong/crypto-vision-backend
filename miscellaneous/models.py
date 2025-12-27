from django.contrib.auth.models import User
from django.db import models


class ErrorLog(models.Model):
    type = models.CharField(max_length=50)
    endpoint = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    message = models.TextField()
    stack_trace = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User,
        # settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="error_logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"[{self.timestamp}] {self.type} - {self.endpoint or 'N/A'}"
