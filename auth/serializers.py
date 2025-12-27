from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name",
                  "last_name", "avatar_url", "is_staff",)

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        profile = getattr(obj, "profile", None)
        if profile and profile.avatar:
            url = profile.avatar.url
            return request.build_absolute_uri(url) if request else url
        return None
