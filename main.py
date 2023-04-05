import os
import json

import requests

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def respond_with_text(response, chat_id):
    url = BASE_URL + "/sendMessage"
    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    return requests.post(url, data)


chat_id = 563198740
url = BASE_URL + "/sendMessage"

data = {
    'text': 'Your routes:',
    'chat_id': 563198740,
    'reply_markup':
        {
            "inline_keyboard":
                [
                    [
                        {"text": "back", "callback_data": "hello world!"}
                    ]
                ]
        }
}


response = requests.post(url, json=data)

print(response.status_code)
print(response.text)

