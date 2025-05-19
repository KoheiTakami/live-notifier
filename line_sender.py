import os
import requests
from dotenv import load_dotenv

def send_line_push(message):
    load_dotenv()
    access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    body = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)
    print("✅ LINE通知ステータス:", response.status_code)
    print(response.text)

__all__ = ['send_line_push']
