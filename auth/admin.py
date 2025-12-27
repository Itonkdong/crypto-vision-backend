from django.contrib import admin

from auth.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_email', 'user_date_joined', 'has_avatar']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    list_filter = ['user__date_joined', 'user__is_active']
    ordering = ['user__username']

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('avatar',)
        }),
    )

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'

    def user_date_joined(self, obj):
        return obj.user.date_joined

    user_date_joined.short_description = 'Date Joined'
    user_date_joined.admin_order_field = 'user__date_joined'

    def has_avatar(self, obj):
        return bool(obj.avatar)

    has_avatar.boolean = True
    has_avatar.short_description = 'Avatar'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
