import os
import json

from src.constructor.services.vehicle_crud import get_user_vehicles

import requests

TOKEN = os.environ['BOT_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def respond_with_text(response, chat_id):
    url = BASE_URL + "/sendMessage"
    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    return requests.post(url, data)


chat_id = 539261624
url = BASE_URL + "/sendMessage"

# data = {
#     'text': 'Your routes:',
#     'chat_id': 563198740,
#     'reply_markup':
#         {'inline_keyboard': [[{'text': 'back', 'callback_data': 'back'}, {'text': 'next', 'callback_data': 'next'}],
#                              [{'text': 'ROUTE#d958f7c0-00ff-49e7-b019-f093fc9e29d9', 'callback_data': 'wow'}]]}
# }

# print(respond_with_text("круто игнорим, обещали сообщить когда будете", chat_id).status_code)
# print(response.status_code)
# print(response.text)

#
# def update_inline_keyboard(
#         chat_id: int,
#         message_id: int,
#         keyboard_definition: dict,
# ):
#     print(keyboard_definition)
#     keyboard_definition = json.dumps(keyboard_definition)
#     url = BASE_URL + f"/editMessageReplyMarkup"
#     data = {
#         "chat_id": chat_id,
#         "message_id": message_id,
#         "reply_markup": keyboard_definition,
#     }
#     response = requests.post(url, data)
#     print(response.status_code, response.text)
#
#
# update_inline_keyboard(chat_id, response.json()['result']["message_id"], {
#     'inline_keyboard': [[{'text': 'back', 'callback_data': 'back'}, {'text': 'nextt', 'callback_data': 'next'}],
#                         [{'text': 'ROUTE#d958f7c0-00ff-49e7-b019-f093fc9e29d9', 'callback_data': 'wow'}]]})
#

response = get_user_vehicles(username="ddakib")
print(response)