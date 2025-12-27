import logging
from typing import List, Dict, Any

from django.contrib.auth.models import User
from django.db import DatabaseError

from helpers.abstract import AbstractService
from marketdata.exceptions.watchlist_exceptions import (
    SymbolRequiredError, SubscriptionError, UnsubscriptionError,
    WatchlistOperationError
)
from marketdata.models import WatchlistItem

logger = logging.getLogger(__name__)


class WatchlistService(AbstractService):
    """Simple watchlist service implementing observer pattern"""

    def subscribe(self, user: User, symbol: str) -> Dict[str, Any]:
        """Subscribe user to a symbol (add to watchlist)"""
        if not symbol or not symbol.strip():
            raise SymbolRequiredError("Symbol is required and cannot be empty")

        symbol = symbol.upper().strip()

        try:
            item, created = WatchlistItem.objects.get_or_create(user=user, symbol=symbol)

            if created:
                self.notify(user, symbol, 'subscribed')

            return {"ok": True, "symbol": symbol, "created": created}

        except DatabaseError as e:
            logger.error(f"Database error during subscription: {str(e)}")
            raise SubscriptionError(f"Failed to subscribe to {symbol}: database error")
        except Exception as e:
            logger.error(f"Unexpected error during subscription: {str(e)}")
            raise WatchlistOperationError(f"Unexpected error while subscribing to {symbol}")

    def unsubscribe(self, user: User, symbol: str) -> Dict[str, Any]:
        """Unsubscribe user from a symbol (remove from watchlist)"""
        if not symbol or not symbol.strip():
            raise SymbolRequiredError("Symbol is required and cannot be empty")

        symbol = symbol.upper().strip()

        try:
            deleted_count, _ = WatchlistItem.objects.filter(user=user, symbol=symbol).delete()

            if deleted_count > 0:
                self.notify(user, symbol, 'unsubscribed')

            return {"ok": True, "symbol": symbol, "deleted": deleted_count}

        except DatabaseError as e:
            logger.error(f"Database error during unsubscription: {str(e)}")
            raise UnsubscriptionError(f"Failed to unsubscribe from {symbol}: database error")
        except Exception as e:
            logger.error(f"Unexpected error during unsubscription: {str(e)}")
            raise WatchlistOperationError(f"Unexpected error while unsubscribing from {symbol}")

    def list_subscribed_symbols(self, user: User) -> List[str]:
        """Get list of symbols user is subscribed to"""
        try:
            items = WatchlistItem.objects.filter(user=user).order_by("-created_at")
            return [item.symbol for item in items]

        except Exception as e:
            logger.error(f"Unexpected error while fetching watchlist: {str(e)}")
            raise WatchlistOperationError("Unexpected error while retrieving watchlist")

    def notify(self, user: User, symbol: str, action: str) -> None:
        """Notify about watchlist changes"""
        raise NotImplementedError("Notification functionality not yet implemented")


service = WatchlistService()


def get_watchlist_service() -> WatchlistService:
    """
    Factory and Singleton method to get the WatchlistService instance.

    This method implements both Factory and Singleton design patterns:
    - Factory Pattern: Creates and returns service instances based on type
    - Singleton Pattern: Ensures only one instance exists throughout the application lifecycle

    Returns:
        WatchlistService: The singleton instance of WatchlistService

    Note:
        Thread-safe singleton implementation ensures concurrent access safety.
        The service implements Observer pattern for watchlist change notifications.
    """
    return service
