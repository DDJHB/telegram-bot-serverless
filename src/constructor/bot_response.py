import os

import requests


TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def respond_with_text(response, chat_id):
    url = BASE_URL + "/sendMessage"
    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    requests.post(url, data)


def respond_with_map(chat_id):
    url = BASE_URL + "/sendLocation"
    data = {
        "chat_id": chat_id,
        "latitude": 40.391246,
        "longitude": 49.856354,
    }
    requests.post(url, data)
