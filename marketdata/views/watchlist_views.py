from typing import Any

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from marketdata.services.watchlist_service import get_watchlist_service


class WatchlistListView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.watchlist_service = get_watchlist_service()

    def get(self, request):
        """Get all watchlist items for the authenticated user"""
        symbols = self.watchlist_service.list_subscribed_symbols(request.user)
        return Response({"symbols": symbols})


class WatchlistAddView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.watchlist_service = get_watchlist_service()

    def post(self, request):
        """Add a symbol to the user's watchlist"""
        symbol = request.data.get("symbol", "")

        result = self.watchlist_service.subscribe(request.user, symbol)
        return Response(result)


class WatchlistRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.watchlist_service = get_watchlist_service()

    def post(self, request):
        """Remove a symbol from the user's watchlist"""
        symbol = request.data.get("symbol", "")

        result = self.watchlist_service.unsubscribe(request.user, symbol)
        return Response(result)

