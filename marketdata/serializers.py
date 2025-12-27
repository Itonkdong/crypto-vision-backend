from rest_framework import serializers

from .models import Price, SupportedCoin
from .models import PriceAlert


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = [
            "symbol", "yahoo_symbol", "ts_readable", "open", "high", "low", "close",
            "adj_close", "volume", "liquidity",
        ]


class PriceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceAlert
        fields = ['id', 'crypto', 'symbol', 'condition', 'price', 'active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SupportedCoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportedCoin
        fields = ['id', 'name', 'symbol']
