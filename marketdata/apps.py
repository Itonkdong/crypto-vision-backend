import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class MarketdataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketdata'
