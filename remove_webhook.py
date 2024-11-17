import requests
import os
def remove_webhook(token):
    webhook_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
    response = requests.get(webhook_url)
    return response.json()

BOT_TOKEN  = os.environ.get("CHATBOT_TOKEN")
response = remove_webhook(BOT_TOKEN)
print(response)
