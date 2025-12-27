from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from marketdata.models import PriceAlert, Price
from auth.services.email_service import send_alert_email
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check price alerts and send notifications when conditions are met'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting alert check...'))
        
        active_alerts = PriceAlert.objects.filter(active=True)
        self.stdout.write(f'Found {active_alerts.count()} active alerts')
        
        checked_count = 0
        triggered_count = 0
        
        for alert in active_alerts:
            try:
                # Check if we should skip due to recent notification
                if alert.last_sent_at:
                    time_since_last_sent = timezone.now() - alert.last_sent_at
                    if time_since_last_sent < timedelta(hours=24):
                        # Log but don't count as "checked" in a way that implies failure, strictly skipping
                        self.stdout.write(f'Skipping {alert.symbol} for user {alert.user.username} - email sent {time_since_last_sent.total_seconds() / 3600:.1f} hours ago')
                        continue
                
                current_price = self.get_current_price(alert.symbol)
                
                if current_price is None:
                    self.stdout.write(self.style.WARNING(f'Could not fetch price for {alert.symbol}'))
                    continue
                
                checked_count += 1
                
                condition_met = False
                if alert.condition == 'above' and current_price >= float(alert.price):
                    condition_met = True
                elif alert.condition == 'below' and current_price <= float(alert.price):
                    condition_met = True
                
                if condition_met:
                    self.stdout.write(f'Alert condition met for {alert.symbol}: {current_price} {alert.condition} {alert.price}')
                    
                    # Check if user has an email address
                    if not alert.user.email or not alert.user.email.strip():
                        self.stdout.write(self.style.WARNING(
                            f'⚠ Skipping email for {alert.symbol} - user {alert.user.username} has no email address'
                        ))
                        continue
                    
                    success = send_alert_email(
                        user_email=alert.user.email,
                        crypto_name=alert.crypto,
                        symbol=alert.symbol,
                        condition=alert.condition,
                        target_price=float(alert.price),
                        current_price=current_price
                    )
                    
                    if success:
                        alert.is_triggered = True
                        alert.last_triggered_at = timezone.now()
                        alert.last_sent_at = timezone.now()
                        alert.save()
                        
                        triggered_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Alert triggered and email sent: {alert.symbol} {alert.condition} ${alert.price} (current: ${current_price:.2f})'
                        ))
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to send email for {alert.symbol}'))
                
            except Exception as e:
                logger.error(f'Error checking alert {alert.id}: {str(e)}')
                self.stdout.write(self.style.ERROR(f'Error checking alert {alert.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nAlert check complete: {checked_count} checked, {triggered_count} triggered'
        ))
    
    def get_current_price(self, symbol):
        """Fetch current price directly from the Price model"""
        try:
            # simple usage of filter/order_by to get latest price
            # assuming ts_readable is reliable sort or use 'ts' (timestamp)
            latest_price = Price.objects.filter(symbol=symbol).order_by('-ts_readable').first()
            
            if latest_price:
                # Prioritize 'close', then 'adj_close'
                price = latest_price.close if latest_price.close is not None else latest_price.adj_close
                return price
            
            return None
            
        except Exception as e:
            logger.error(f'Error fetching price for {symbol}: {str(e)}')
            return None
