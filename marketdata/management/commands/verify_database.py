from django.core.management.base import BaseCommand
from helpers.db_utils import verify_database_integrity


class Command(BaseCommand):
    help = 'Verify database integrity (run this after git pull)'

    def handle(self, *args, **options):
        self.stdout.write('Verifying database integrity...')
        
        if verify_database_integrity():
            self.stdout.write(self.style.SUCCESS('[OK] Database is healthy!'))
        else:
            self.stdout.write(self.style.ERROR('[ERROR] Database is CORRUPTED!'))
            self.stdout.write('\nTo fix:')
            self.stdout.write('1. Restore from previous commit: git checkout HEAD~1 -- "Домашна 1/crypto.db"')
            self.stdout.write('2. Or get a fresh copy from a teammate')
            self.stdout.write('3. Or restore from backup')

