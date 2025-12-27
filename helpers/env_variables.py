import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DB_NAME = os.environ.get('DB_NAME', 'crypto.db')

# Allowed Hosts Configuration
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Email Configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-app-password')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Crypto Dashboard <noreply@cryptodashboard.com>')

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000').split(',')

# Twitter API Configuration
TWITTER_BEARER_TOKEN = os.environ.get('TWITTER_BEARER_TOKEN', '')

# Microservices Base URLs
TECHNICAL_ANALYSIS_SERVICE_URL = os.environ.get('TECHNICAL_ANALYSIS_SERVICE_URL', 'http://localhost:8001')
LSTM_SERVICE_URL = os.environ.get('LSTM_SERVICE_URL', 'http://localhost:8002')
SENTIMENT_ANALYSIS_SERVICE_URL = os.environ.get('SENTIMENT_ANALYSIS_SERVICE_URL', 'http://localhost:8003')
NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL', 'http://localhost:8004')

