from django.contrib.auth.models import User
from django.db import models


class Price(models.Model):
    rowid = models.BigIntegerField(primary_key=True, db_column="rowid")
    symbol = models.CharField(max_length=64, db_column="symbol")
    yahoo_symbol = models.CharField(max_length=64, db_column="yahoo_symbol")
    ts_readable = models.CharField(max_length=64, null=True, blank=True, db_column="ts_readable")
    open = models.FloatField(null=True, blank=True, db_column="open")
    high = models.FloatField(null=True, blank=True, db_column="high")
    low = models.FloatField(null=True, blank=True, db_column="low")
    close = models.FloatField(null=True, blank=True, db_column="close")
    adj_close = models.FloatField(null=True, blank=True, db_column="adj_close")
    volume = models.FloatField(null=True, blank=True, db_column="volume")
    liquidity = models.FloatField(null=True, blank=True, db_column="liquidity")

    class Meta:
        managed = False
        db_table = "prices"
        ordering = ["-ts_readable"]

    def __str__(self) -> str:
        return f"{self.symbol} @ {self.ts_readable}"


class PriceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_alerts')
    crypto = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    condition = models.CharField(max_length=10, choices=[('above', 'Above'), ('below', 'Below')])
    price = models.DecimalField(max_digits=20, decimal_places=2)
    active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.crypto} {self.condition} ${self.price}"


class SupportedCoin(models.Model):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_items")
    symbol = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "symbol")

    def __str__(self):
        return f"{self.user.username} -> {self.symbol}"

