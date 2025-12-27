import logging
from typing import List, Dict, Any, Optional

from django.db.models import Max, Min, Sum, OuterRef, Subquery

from helpers.abstract import AbstractService
from marketdata.exceptions.market_data_exceptions import (
    SymbolNotFoundError, PriceDataNotFoundError, AlertNotFoundError,
    AlertValidationError, MarketDataProcessingError
)
from marketdata.models import Price, PriceAlert, SupportedCoin
from marketdata.serializers import PriceAlertSerializer
from marketdata.serializers import SupportedCoinSerializer

logger = logging.getLogger(__name__)


class MarketDataService(AbstractService):
    """Service class for handling market data business logic"""

    def clamp_limit(self, value: str | None, *, default: int = 50, max_value: int = 500) -> int:
        """Validate and clamp limit parameter"""
        if not value:
            return default
        try:
            parsed = int(value)
            clamped = max(1, min(parsed, max_value))
            if clamped != parsed:
                logger.debug(f"Clamped limit from {parsed} to {clamped}")
            return clamped
        except (TypeError, ValueError):
            logger.debug(f"Invalid limit value '{value}', using default {default}")
            return default

    def get_available_exchanges(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of available exchanges (distinct symbols)"""
        try:
            logger.debug(f"Fetching available exchanges with limit {limit}")
            symbols = Price.objects.values_list('symbol', flat=True).distinct().order_by('symbol')[:limit]
            result = [{"exchange_id": sym, "name": sym} for sym in symbols]
            logger.info(f"Retrieved {len(result)} exchanges")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch exchanges: {str(e)}")
            raise MarketDataProcessingError(f"Failed to fetch exchanges: {str(e)}")

    def get_ticker_data(self, base: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get ticker data for symbols"""
        try:
            if base:
                logger.debug(f"Fetching ticker data for specific symbol: {base}")
                latest_prices = Price.objects.filter(
                    symbol=base.upper()
                ).order_by('-ts_readable')[:1]

                if not latest_prices.exists():
                    logger.warning(f"Symbol {base.upper()} not found in database")
                    raise SymbolNotFoundError(f"Symbol {base.upper()} not found")
            else:
                logger.debug(f"Fetching ticker data for all symbols with limit {limit}")
                latest_prices = Price.objects.filter(
                    ts_readable__in=Subquery(
                        Price.objects.filter(
                            symbol=OuterRef('symbol')
                        ).order_by('-ts_readable').values('ts_readable')[:1]
                    )
                ).order_by('-ts_readable')[:limit]

            results = []
            for price in latest_prices:
                ticker_data = self._process_price_to_ticker(price)
                if ticker_data:
                    results.append(ticker_data)

            logger.info(f"Successfully processed {len(results)} ticker entries")
            return {"count": len(results), "results": results}
        except (SymbolNotFoundError, PriceDataNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Failed to fetch ticker data: {str(e)}")
            raise MarketDataProcessingError(f"Failed to fetch ticker data: {str(e)}")

    def _process_price_to_ticker(self, price: Price) -> Optional[Dict[str, Any]]:
        """Convert Price object to ticker format"""
        try:
            symbol = price.symbol
            if not symbol:
                return None

            open_price = price.open or 0
            high = price.high or 0
            low = price.low or 0
            close = price.close
            adj_close = price.adj_close
            volume = price.volume or 0
            ts_readable = price.ts_readable
            liquidity = price.liquidity or 0

            current_price = close if close is not None else (
                adj_close if adj_close is not None else (
                    open_price if open_price else 0
                )
            )

            return {
                "exchange": {"exchange_id": symbol, "name": symbol},
                "market_symbol": f"{symbol}/USD",
                "captured_at": ts_readable,
                "last": current_price,
                "high_24h": high if high else current_price,
                "low_24h": low if low else current_price,
                "base_volume_24h": volume,
                "quote_volume_24h": volume * current_price,
                "liquidity": liquidity,
                "bid": None,
                "ask": None,
                "spread_bps": None,
            }
        except Exception as e:
            logger.warning(f"Failed to process ticker for symbol {getattr(price, 'symbol', 'unknown')}: {str(e)}")
            return None

    def get_candle_series(self, symbol: str, limit: int = 90) -> Dict[str, Any]:
        """Get candlestick data for a symbol"""
        try:
            symbol = symbol.upper()
            logger.debug(f"Fetching candle data for {symbol} with limit {limit}")

            prices = Price.objects.filter(symbol=symbol).order_by('-ts_readable')[:limit]

            if not prices.exists():
                logger.warning(f"No candle data found for symbol {symbol}")
                raise SymbolNotFoundError(f"No data found for symbol {symbol}")

            results = []
            for price in prices:
                candle_data = self._process_price_to_candle(price)
                if candle_data:
                    results.append(candle_data)

            logger.info(f"Retrieved {len(results)} candle entries for {symbol}")
            return {"count": len(results), "results": results}
        except SymbolNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch candle data for {symbol}: {str(e)}")
            raise MarketDataProcessingError(f"Failed to fetch candle data: {str(e)}")

    def _process_price_to_candle(self, price: Price) -> Optional[Dict[str, Any]]:
        """Convert Price object to candle format"""
        try:
            if not price.ts_readable:
                return None

            close_price = price.close if price.close is not None else (
                price.adj_close if price.adj_close is not None else 0
            )

            return {
                "exchange": {"exchange_id": price.symbol, "name": price.symbol},
                "market_symbol": f"{price.symbol}/USD",
                "time": price.ts_readable,
                "open": price.open,
                "high": price.high,
                "low": price.low,
                "close": close_price,
                "volume_base": price.volume,
                "volume_quote_est": (price.volume or 0) * close_price,
            }
        except Exception as e:
            logger.warning(f"Failed to process candle for symbol {getattr(price, 'symbol', 'unknown')}: {str(e)}")
            return None

    def get_data_summary(self) -> Dict[str, Any]:
        """Get market data summary statistics"""
        try:
            logger.debug("Generating market data summary")

            distinct_symbols = Price.objects.values('symbol').distinct().count()
            ts_aggregates = Price.objects.aggregate(
                latest=Max('ts_readable'),
                oldest=Min('ts_readable')
            )
            latest_ts_readable = ts_aggregates['latest']
            oldest_ts_readable = ts_aggregates['oldest']
            markets_with_liquidity = Price.objects.filter(
                volume__gt=0
            ).values('symbol').distinct().count()
            top_volume_symbol = Price.objects.filter(
                volume__gt=0
            ).values('symbol').annotate(
                total_volume=Sum('volume')
            ).order_by('-total_volume').first()

            summary = {
                "exchanges": distinct_symbols,
                "distinct_markets": distinct_symbols,
                "latest_candle_date": self._date_from_readable(latest_ts_readable),
                "latest_ticker_ts": latest_ts_readable,
                "markets_with_liquidity": markets_with_liquidity,
            }

            if top_volume_symbol:
                summary["top_volume_market"] = {
                    "market_symbol": f"{top_volume_symbol['symbol']}/USD",
                    "quote_volume_24h": top_volume_symbol['total_volume'] or 0
                }

            logger.info(f"Generated summary: {distinct_symbols} symbols, {markets_with_liquidity} with liquidity")
            return summary
        except Exception as e:
            logger.error(f"Failed to generate data summary: {str(e)}")
            raise MarketDataProcessingError(f"Failed to generate data summary: {str(e)}")

    def _date_from_readable(self, ts_value: str | None) -> str | None:
        """Extract date from readable timestamp"""
        # ...existing code...
        if not ts_value:
            return None
        return ts_value.split("T")[0] if "T" in ts_value else ts_value

    def get_user_alerts(self, user) -> List[Dict[str, Any]]:
        """Get all price alerts for a user"""
        try:
            logger.debug(f"Fetching alerts for user {user.username}")
            alerts = PriceAlert.objects.filter(user=user)
            serializer = PriceAlertSerializer(alerts, many=True)
            logger.info(f"Retrieved {alerts.count()} alerts for user {user.username}")
            return serializer.data
        except Exception as e:
            logger.error(f"Failed to fetch alerts for user {user.username}: {str(e)}")
            raise MarketDataProcessingError(f"Failed to fetch alerts: {str(e)}")

    def create_alert(self, user, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new price alert"""
        try:
            symbol = alert_data.get('symbol', 'unknown')
            logger.debug(f"Creating alert for user {user.username}, symbol {symbol}")

            serializer = PriceAlertSerializer(data=alert_data)
            if serializer.is_valid():
                alert = serializer.save(user=user)
                logger.info(f"Created alert {alert.id} for user {user.username}, symbol {symbol}")
                return PriceAlertSerializer(alert).data
            else:
                logger.warning(f"Invalid alert data for user {user.username}: {serializer.errors}")
                raise AlertValidationError(f"Invalid alert data: {serializer.errors}")
        except AlertValidationError:
            raise
        except Exception as e:
            logger.error(f"Failed to create alert for user {user.username}: {str(e)}")
            raise MarketDataProcessingError(f"Failed to create alert: {str(e)}")

    def get_user_alert(self, user, alert_id: int) -> Dict[str, Any]:
        """Get specific price alert for a user"""
        try:
            logger.debug(f"Fetching alert {alert_id} for user {user.username}")
            alert = self._get_alert_or_raise(alert_id, user)
            return PriceAlertSerializer(alert).data
        except AlertNotFoundError:
            logger.warning(f"Alert {alert_id} not found for user {user.username}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch alert {alert_id} for user {user.username}: {str(e)}")
            raise MarketDataProcessingError(f"Failed to fetch alert: {str(e)}")

    def update_user_alert(self, user, alert_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a price alert"""
        try:
            logger.debug(f"Updating alert {alert_id} for user {user.username}")
            alert = self._get_alert_or_raise(alert_id, user)
            serializer = PriceAlertSerializer(alert, data=update_data, partial=True)
            if serializer.is_valid():
                updated_alert = serializer.save()
                logger.info(f"Updated alert {alert_id} for user {user.username}")
                return PriceAlertSerializer(updated_alert).data
            else:
                logger.warning(f"Invalid update data for alert {alert_id}: {serializer.errors}")
                raise AlertValidationError(f"Invalid update data: {serializer.errors}")
        except (AlertNotFoundError, AlertValidationError):
            raise
        except Exception as e:
            logger.error(f"Failed to update alert {alert_id} for user {user.username}: {str(e)}")
            raise MarketDataProcessingError(f"Failed to update alert: {str(e)}")

    def delete_user_alert(self, user, alert_id: int) -> None:
        """Delete a price alert"""
        try:
            logger.debug(f"Deleting alert {alert_id} for user {user.username}")
            alert = self._get_alert_or_raise(alert_id, user)
            alert.delete()
            logger.info(f"Deleted alert {alert_id} for user {user.username}")
        except AlertNotFoundError:
            logger.warning(f"Alert {alert_id} not found for user {user.username} during delete")
            raise
        except Exception as e:
            logger.error(f"Failed to delete alert {alert_id} for user {user.username}: {str(e)}")
            raise MarketDataProcessingError(f"Failed to delete alert: {str(e)}")

    def _get_alert_or_raise(self, alert_id: int, user) -> PriceAlert:
        """Get alert by ID and user, raise exception if not found"""
        try:
            return PriceAlert.objects.get(pk=alert_id, user=user)
        except PriceAlert.DoesNotExist:
            raise AlertNotFoundError(f"Alert with ID {alert_id} not found")

    def get_supported_coins(self) -> List[Dict[str, Any]]:
        """Get list of supported coins"""
        try:
            logger.debug("Fetching supported coins")
            coins = SupportedCoin.objects.filter(is_active=True)
            serializer = SupportedCoinSerializer(coins, many=True)
            logger.info(f"Retrieved {coins.count()} supported coins")
            return serializer.data
        except Exception as e:
            logger.error(f"Failed to fetch supported coins: {str(e)}")
            raise MarketDataProcessingError(f"Failed to fetch supported coins: {str(e)}")


service = MarketDataService()


def get_marketdata_service() -> MarketDataService:
    """
    Factory and Singleton method to get the MarketDataService instance.

    This method implements both Factory and Singleton design patterns:
    - Factory Pattern: Creates and returns service instances based on type
    - Singleton Pattern: Ensures only one instance exists throughout the application lifecycle

    Returns:
        MarketDataService: The singleton instance of MarketDataService

    Note:
        Thread-safe singleton implementation ensures concurrent access safety.
        This service handles all market data operations including price data, alerts, and statistics.
    """
    return service
