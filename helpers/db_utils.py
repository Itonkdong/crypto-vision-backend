"""
Database utilities to handle database operations safely
"""
import sqlite3
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_sqlite_connection():
    """
    Get a SQLite connection with proper settings to prevent corruption.
    """
    db_path = settings.DATABASES['default']['NAME']
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    
    # Set SQLite pragmas to prevent corruption
    # WAL mode is especially important for Git operations
    conn.execute('PRAGMA journal_mode=WAL;')  # Write-Ahead Logging (more resilient)
    conn.execute('PRAGMA synchronous=NORMAL;')  # Balance between safety and speed
    conn.execute('PRAGMA foreign_keys=ON;')  # Enable foreign key constraints
    conn.execute('PRAGMA busy_timeout=30000;')  # Wait up to 30 seconds for locks
    
    return conn


def verify_database_integrity():
    """
    Verify database integrity - call this after git pull
    """
    db_path = Path(settings.DATABASES['default']['NAME'])
    
    if not db_path.exists():
        logger.warning(f"Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path), timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('PRAGMA integrity_check;')
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 'ok':
            logger.info("Database integrity check passed")
            return True
        else:
            logger.error(f"Database integrity check failed: {result}")
            return False
    except Exception as e:
        logger.error(f"Error checking database integrity: {e}")
        return False
