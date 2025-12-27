from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketdata.models import PriceAlert


class Command(BaseCommand):
    help = 'Check which users have email addresses and which alerts might not send emails'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking user email addresses...\n'))
        
        all_users = User.objects.all()
        users_without_email = []
        users_with_email = []
        
        for user in all_users:
            if not user.email or not user.email.strip():
                users_without_email.append(user)
            else:
                users_with_email.append(user)
        
        self.stdout.write(f'Total users: {all_users.count()}')
        self.stdout.write(self.style.SUCCESS(f'Users WITH email: {len(users_with_email)}'))
        self.stdout.write(self.style.WARNING(f'Users WITHOUT email: {len(users_without_email)}\n'))
        
        if users_without_email:
            self.stdout.write(self.style.ERROR('Users without email addresses:'))
            for user in users_without_email:
                alert_count = PriceAlert.objects.filter(user=user, active=True).count()
                self.stdout.write(f'  - {user.username} (ID: {user.id}) - {alert_count} active alerts')
        
        # Check alerts that won't send emails
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Active alerts that WON\'T send emails (user has no email):')
        self.stdout.write('='*60)
        
        alerts_without_email = PriceAlert.objects.filter(active=True).select_related('user')
        count = 0
        for alert in alerts_without_email:
            if not alert.user.email or not alert.user.email.strip():
                count += 1
                self.stdout.write(
                    f'  Alert #{alert.id}: {alert.symbol} {alert.condition} ${alert.price} '
                    f'for user "{alert.user.username}" (no email)'
                )
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('  ✓ All active alerts have users with email addresses'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠ {count} active alerts will not send emails because users have no email addresses'))

