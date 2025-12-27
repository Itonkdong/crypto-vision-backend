from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Set email address for a user who doesn\'t have one'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('email', type=str, help='Email address to set')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        
        try:
            user = User.objects.get(username=username)
            
            if user.email and user.email.strip():
                self.stdout.write(
                    self.style.WARNING(
                        f'User {username} already has an email: {user.email}'
                    )
                )
                response = input('Do you want to change it? (yes/no): ')
                if response.lower() != 'yes':
                    self.stdout.write('Cancelled.')
                    return
            
            # Check if email is already used by another user
            if User.objects.filter(email=email).exclude(username=username).exists():
                self.stdout.write(
                    self.style.ERROR(
                        f'Email {email} is already used by another user!'
                    )
                )
                return
            
            user.email = email
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully set email {email} for user {username}'
                )
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found!')
            )

