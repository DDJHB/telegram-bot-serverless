import os
import json



import requests

TOKEN = os.environ['BOT_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def respond_with_text(response, chat_id, parse_mode = None):
    url = BASE_URL + "/sendMessage"
    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    if parse_mode:
        data.update({"parse_mode": parse_mode})
    return requests.post(url, data)


chat_id = 563198740
url = BASE_URL + "/sendMessage"

route_info_message = "*hello*"

data = {
    'text': route_info_message,
    'chat_id': 563198740,
}

respond_with_text(route_info_message, chat_id, parse_mode="markdown")