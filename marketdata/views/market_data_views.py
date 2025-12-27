from typing import Any

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from marketdata.models import SupportedCoin
from marketdata.serializers import SupportedCoinSerializer
from marketdata.services.market_data_service import get_marketdata_service


class ExchangeListView(APIView):
    """List available exchanges (symbols)"""
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.marketdata_service = get_marketdata_service()

    def get(self, request):
        results = self.marketdata_service.get_available_exchanges(limit=100)
        return Response({"results": results})


class TickerListView(APIView):
    """Get ticker data for symbols"""
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.marketdata_service = get_marketdata_service()

    def get(self, request):
        base = request.query_params.get("base")
        limit = self.marketdata_service.clamp_limit(
            request.query_params.get("limit"),
            default=50,
            max_value=5000
        )

        data = self.marketdata_service.get_ticker_data(base=base, limit=limit)
        return Response(data)


class CandleSeriesView(APIView):
    """Get candlestick data for a symbol"""
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.marketdata_service = get_marketdata_service()

    def get(self, request, symbol: str):
        limit = self.marketdata_service.clamp_limit(
            request.query_params.get("limit"),
            default=90,
            max_value=1000
        )

        data = self.marketdata_service.get_candle_series(symbol=symbol, limit=limit)
        return Response(data)


class DataSummaryView(APIView):
    """Get market data summary statistics"""
    authentication_classes = []
    permission_classes = []

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.marketdata_service = get_marketdata_service()

    def get(self, request):
        summary = self.marketdata_service.get_data_summary()
        return Response(summary)


class PriceAlertListCreateView(APIView):
    """List and create price alerts"""
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.marketdata_service = get_marketdata_service()

    def get(self, request):
        alerts = self.marketdata_service.get_user_alerts(request.user)
        return Response(alerts)

    def post(self, request):
        alert_data = self.marketdata_service.create_alert(request.user, request.data)
        return Response(alert_data, status=status.HTTP_201_CREATED)


class PriceAlertDetailView(APIView):
    """Retrieve, update and delete price alerts"""
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.marketdata_service = get_marketdata_service()

    def get(self, request, pk):
        alert_data = self.marketdata_service.get_user_alert(request.user, pk)
        return Response(alert_data)

    def put(self, request, pk):
        alert_data = self.marketdata_service.update_user_alert(request.user, pk, request.data)
        return Response(alert_data)

    def delete(self, request, pk):
        self.marketdata_service.delete_user_alert(request.user, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SupportedCoinListView(generics.ListAPIView):
    """List supported coins"""
    serializer_class = SupportedCoinSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        return SupportedCoin.objects.filter(is_active=True)
