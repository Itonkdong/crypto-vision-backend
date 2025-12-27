from rest_framework import serializers

from miscellaneous.models import ErrorLog


class ErrorLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ErrorLog
        fields = ['id', 'type', 'endpoint', 'status', 'message', 'stack_trace', 'user', 'username', 'timestamp']
        read_only_fields = ['id', 'timestamp', 'username']
