import requests
import os
import cv2

def send_telegram_alert(photo_path):
    """Sends a photo and a security alert to your Telegram."""
    token = "8424626832:AAF1VbfAAlh525fbUhW38ln9BuTbHbKzpoM"  # Paste your token from BotFather
    chat_id = "5271774128"  # Paste your ID from userinfobot
    caption = "⚠️ SECURITY BREACH: Unauthorized access attempt detected."
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    with open(photo_path, 'rb') as photo:
        payload = {
            'chat_id': chat_id,
            'caption': caption
        }
        files = {
            'photo': photo
        }
        # Using a POST request to send the actual file buffer
        requests.post(url, data=payload, files=files)