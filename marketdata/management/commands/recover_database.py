from django.core.management.base import BaseCommand
from django.conf import settings
import sqlite3
import shutil
from pathlib import Path
import os


class Command(BaseCommand):
    help = 'Attempt to recover a corrupted SQLite database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create a backup before attempting recovery',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recovery even if database seems OK',
        )

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        db_path = Path(db_path)
        
        self.stdout.write(f'Database path: {db_path}')
        
        if not db_path.exists():
            self.stdout.write(self.style.ERROR(f'Database file not found at {db_path}'))
            return
        
        # Create backup
        if options['backup']:
            backup_path = db_path.with_suffix('.db.backup')
            self.stdout.write(f'Creating backup to {backup_path}...')
            try:
                shutil.copy2(db_path, backup_path)
                self.stdout.write(self.style.SUCCESS(f'✓ Backup created'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create backup: {e}'))
                return
        
        # Try to open and check the database
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute('SELECT 1')
            conn.close()
            if not options['force']:
                self.stdout.write(self.style.SUCCESS('Database appears to be OK. Use --force to attempt recovery anyway.'))
                return
        except sqlite3.DatabaseError as e:
            self.stdout.write(self.style.WARNING(f'Database is corrupted: {e}'))
        
        # Attempt recovery
        self.stdout.write('Attempting to recover database...')
        
        recovered_path = db_path.with_suffix('.db.recovered')
        
        try:
            # Try to dump and recreate
            old_conn = sqlite3.connect(str(db_path))
            new_conn = sqlite3.connect(str(recovered_path))
            
            # Try to get schema
            try:
                schema = old_conn.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
                self.stdout.write(f'Found {len(schema)} tables in schema')
            except:
                self.stdout.write(self.style.WARNING('Could not read schema'))
                schema = []
            
            # Try to recover data
            recovered_tables = 0
            for table_sql in schema:
                if table_sql[0]:
                    try:
                        new_conn.execute(table_sql[0])
                        table_name = table_sql[0].split('(')[0].replace('CREATE TABLE', '').strip()
                        # Try to copy data
                        try:
                            old_conn.backup(new_conn)
                            recovered_tables += 1
                        except:
                            pass
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Could not recover table: {e}'))
            
            old_conn.close()
            new_conn.close()
            
            if recovered_path.exists() and recovered_path.stat().st_size > 0:
                # Replace old database with recovered one
                db_path.unlink()
                recovered_path.rename(db_path)
                self.stdout.write(self.style.SUCCESS(f'✓ Database recovered! Recovered {recovered_tables} tables.'))
                self.stdout.write('You may need to run migrations: python manage.py migrate')
            else:
                self.stdout.write(self.style.ERROR('Recovery failed. Database may be too corrupted.'))
                self.stdout.write('You may need to recreate the database:')
                self.stdout.write('  1. Delete the corrupted database')
                self.stdout.write('  2. Run: python manage.py migrate')
                self.stdout.write('  3. Recreate users and alerts')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Recovery failed: {e}'))
            self.stdout.write('\nYou may need to recreate the database:')
            self.stdout.write('  1. Delete the corrupted database file')
            self.stdout.write('  2. Run: python manage.py migrate')
            self.stdout.write('  3. Recreate users and alerts')

