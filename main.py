import os
import json



import requests

TOKEN = os.environ['BOT_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)

def build_approval_keyboard(item):
    inline_keyboard = [[{"text": "YES", "callback_data": f"YES+{item}"}],
                       [{"text": "NO", "callback_data": f"NO+{item}"}]]

    return {
        "inline_keyboard": inline_keyboard
    }
def respond_with_text(response, chat_id):
    url = BASE_URL + "/sendMessage"
    data = {"text": response.encode("utf8"), "chat_id": chat_id}
    return requests.post(url, data)


chat_id = 563198740
url = BASE_URL + "/sendMessage"

data = {
    'text': 'Your routes:',
    'chat_id': 563198740,
}

response = requests.post(url, json=data)
print(response.status_code, response.text)
message_id = response.json()["result"]["message_id"]
print(message_id)




def build_approval_keyboard(item):
    inline_keyboard = [
        [build_single_route_button(item)],
        [
            {"text": "YES", "callback_data": f"YES+{item.get('route_id', 'random')}"},
            {"text": "NO", "callback_data": f"NO+{item.get('route_id', 'random')}"}
        ]
    ]

    return {
        "inline_keyboard": inline_keyboard
    }