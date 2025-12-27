from django.contrib import admin

from miscellaneous.models import ErrorLog


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'type', 'endpoint', 'status', 'user', 'message_preview']
    list_filter = ['type', 'status', 'timestamp']
    search_fields = ['type', 'endpoint', 'message', 'user__username']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    list_per_page = 25

    fieldsets = (
        ('Error Details', {
            'fields': ('type', 'endpoint', 'status', 'message')
        }),
        ('User & Timing', {
            'fields': ('user', 'timestamp')
        }),
        ('Stack Trace', {
            'fields': ('stack_trace',),
            'classes': ('collapse',)
        }),
    )

    def message_preview(self, obj):
        """Show a truncated version of the message"""
        return (obj.message[:50] + '...') if len(obj.message) > 50 else obj.message

    message_preview.short_description = 'Message Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
