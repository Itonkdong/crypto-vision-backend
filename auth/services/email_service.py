import requests
import logging

logger = logging.getLogger(__name__)


def send_alert_email(user_email, crypto_name, symbol, condition, target_price, current_price):
    """
    Send an email notification via the Notification Microservice.
    """
    if not user_email or not user_email.strip():
        logger.error(f"Cannot send alert email: user email is empty or None")
        return False

    # Notification Service URL
    SERVICE_URL = "http://localhost:8004/send-email"

    try:
        condition_text = "над" if condition == "above" else "под"
        subject = f'🔔 Предупредување за цена: {crypto_name} ({symbol})'

        message = f'''Здраво,

Вашето предупредување за цена е активирано!

Криптовалута: {crypto_name} ({symbol})
Услов: Цена {condition_text} ${target_price:,.2f}
Тековна цена: ${current_price:,.2f}

Ова е автоматска нотификација од вашата Crypto Dashboard апликација.

Поздрав,
Crypto Dashboard Тим
'''

        html_message = f'''
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4;">
                <div style="background-color: #1e293b; color: white; padding: 20px; border-radius: 10px 10px 0 0;">
                    <h2 style="margin: 0;">🔔 Предупредување за цена</h2>
                </div>
                <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px;">Здраво,</p>
                    <p style="font-size: 16px;">Вашето предупредување за цена е активирано!</p>
                    
                    <div style="background-color: #f0f9ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>Криптовалута:</strong> {crypto_name} ({symbol})</p>
                        <p style="margin: 5px 0;"><strong>Услов:</strong> Цена {condition_text} ${target_price:,.2f}</p>
                        <p style="margin: 5px 0;"><strong>Тековна цена:</strong> <span style="color: #3b82f6; font-size: 18px; font-weight: bold;">${current_price:,.2f}</span></p>
                    </div>
                    
                    <p style="font-size: 14px; color: #666;">Ова е автоматска нотификација од вашата Crypto Dashboard апликација.</p>
                    
                    <p style="margin-top: 30px;">Поздрав,<br><strong>Crypto Dashboard Тим</strong></p>
                </div>
            </div>
        </body>
        </html>
        '''

        payload = {
            "subject": subject,
            "body": html_message,
            "recipients": [user_email],
            "is_html": True
        }

        response = requests.post(SERVICE_URL, json=payload)

        if response.status_code == 200:
            logger.info(f"Alert email sent successfully via microservice to {user_email}")
            return True
        else:
            logger.error(f"Notification microservice failed: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Failed to call Notification service: {str(e)}")
        return False
