import requests
from src.constructor.bot_response import respond_with_map


def handler(data):
    respond_with_map(chat_id=data["message"]["chat"]["id"])
    return "Sent the map..."
