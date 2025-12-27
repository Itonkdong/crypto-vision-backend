from django.urls import path

from marketdata.views.sentiment_analysis_views import SentimentOnChainAnalysisView
from marketdata.views.technical_analysis_views import TechnicalAnalysisView

from marketdata.views.market_data_views import SupportedCoinListView, CandleSeriesView, TickerListView, \
    ExchangeListView, DataSummaryView, PriceAlertListCreateView, PriceAlertDetailView

from marketdata.views.lstm_views import LSTMPredictionView
from marketdata.views.watchlist_views import WatchlistListView, WatchlistAddView, WatchlistRemoveView

app_name = "marketdata"

urlpatterns = [

    path("exchanges/", ExchangeListView.as_view(), name="exchanges"),
    path("tickers/", TickerListView.as_view(), name="tickers"),
    path("candles/<str:symbol>/", CandleSeriesView.as_view(), name="candles"),
    path('supported-coins/', SupportedCoinListView.as_view(), name='supported-coins'),
    path("summary/", DataSummaryView.as_view(), name="summary"),

    path("alerts/", PriceAlertListCreateView.as_view(), name="alert_list_create"),
    path("alerts/<int:pk>/", PriceAlertDetailView.as_view(), name="alert_detail"),

    path("technical-analysis/<str:symbol>/", TechnicalAnalysisView.as_view(), name="technical_analysis"),

    path("analysis/<str:symbol>/", SentimentOnChainAnalysisView.as_view(), name="sentiment_onchain_analysis"),
    path("predict/lstm/<str:symbol>/", LSTMPredictionView.as_view(), name="lstm_prediction"),

    path("watchlist/", WatchlistListView.as_view(), name="watchlist_list"),
    path("watchlist/add/", WatchlistAddView.as_view(), name="watchlist_add"),
    path("watchlist/remove/", WatchlistRemoveView.as_view(), name="watchlist_remove"),

]
