from django.contrib import admin
from .models import Price, PriceAlert, SupportedCoin, WatchlistItem


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'yahoo_symbol', 'ts_readable', 'open', 'high', 'low', 'close', 'volume']
    list_filter = ['symbol', 'ts_readable']
    search_fields = ['symbol', 'yahoo_symbol']
    readonly_fields = ['rowid']  # Primary key should be readonly
    ordering = ['-ts_readable']
    list_per_page = 50

    fieldsets = (
        ('Basic Info', {
            'fields': ('rowid', 'symbol', 'yahoo_symbol', 'ts_readable')
        }),
        ('Price Data', {
            'fields': ('open', 'high', 'low', 'close', 'adj_close')
        }),
        ('Volume & Liquidity', {
            'fields': ('volume', 'liquidity')
        }),
    )


@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'crypto', 'symbol', 'condition', 'price', 'active', 'is_triggered', 'created_at']
    list_filter = ['condition', 'active', 'is_triggered', 'created_at', 'symbol']
    search_fields = ['user__username', 'crypto', 'symbol']
    readonly_fields = ['created_at', 'updated_at', 'last_triggered_at', 'last_sent_at']
    ordering = ['-created_at']
    list_per_page = 25

    fieldsets = (
        ('Alert Details', {
            'fields': ('user', 'crypto', 'symbol', 'condition', 'price')
        }),
        ('Status', {
            'fields': ('active', 'is_triggered')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_triggered_at', 'last_sent_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SupportedCoin)
class SupportedCoinAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'symbol']
    ordering = ['name']
    list_editable = ['is_active']  # Allow quick editing of active status

    fieldsets = (
        ('Coin Details', {
            'fields': ('name', 'symbol', 'is_active')
        }),
    )


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'symbol', 'created_at']
    list_filter = ['symbol', 'created_at']
    search_fields = ['user__username', 'symbol']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Watchlist Details', {
            'fields': ('user', 'symbol', 'created_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Optional: Customize the admin site header and title
admin.site.site_header = "Crypto Dashboard Admin"
admin.site.site_title = "Crypto Admin"
admin.site.index_title = "Welcome to Crypto Dashboard Administration"
