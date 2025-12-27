from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a test user for authentication testing'

    def handle(self, *args, **kwargs):
        username = 'testuser'
        password = 'testpass123'
        email = 'test@example.com'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists'))
        else:
            User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created user "{username}"'))
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
