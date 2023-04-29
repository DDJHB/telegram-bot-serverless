import os
import json

import requests

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def respond_with_text(response, chat_id, parse_mode: str = None):
    url = BASE_URL + "/sendMessage"
    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    if parse_mode:
        data.update({"parse_mode": parse_mode})
    requests.post(url, data)


def respond_with_map(chat_id):
    url = BASE_URL + "/sendLocation"
    data = {
        "chat_id": chat_id,
        "latitude": 40.391246,
        "longitude": 49.856354,
    }
    requests.post(url, data)


def respond_with_inline_keyboard(
        parent_message: str,
        keyboard_definition: dict,
        chat_id: int,
):
    url = BASE_URL + "/sendMessage"
    data = {
        "text": parent_message,
        "chat_id": chat_id,
        "reply_markup": json.dumps(keyboard_definition),
    }
    print(data)
    response = requests.post(url, data)
    print(response.status_code, response.text)

    return response


def delete_message(chat_id: str, message_id: str):
    url = BASE_URL + "/deleteMessage"
    data = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    requests.post(url, json=data)


def update_inline_keyboard(
        chat_id: int,
        message_id: int,
        keyboard_definition: dict,
):
    keyboard_definition = json.dumps(keyboard_definition)
    url = BASE_URL + f"/editMessageReplyMarkup"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": keyboard_definition,
    }
    response = requests.post(url, data)
    print(response.status_code, response.text)
