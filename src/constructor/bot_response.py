import os

import requests


TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def respond_with_text(response, chat_id):
    url = BASE_URL + "/sendMessage"
    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    requests.post(url, data)
