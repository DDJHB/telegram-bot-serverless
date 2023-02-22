import json
import os
from http import HTTPStatus

import requests


TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def greet(event, context):
    try:
        data = json.loads(event["body"])
        message = str(data["message"]["text"])
        chat_id = data["message"]["chat"]["id"]
        first_name = data["message"]["chat"]["first_name"]

        response = "Please /start, {}".format(first_name)

        if "/start" in message:
            response = "Hello {}".format(first_name)

        data = {"text": response.encode("utf8"), "chat_id": chat_id}
        url = BASE_URL + "/sendMessage"
        requests.post(url, data)
        return {'statusCode': HTTPStatus.OK}
    except Exception as e:
        print(e)
        requests.post(
            url="https://eow4z7ghug68ys0.m.pipedream.net",
            data=e
        )
        return {'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'body': {"message": "Internal Server Error"}}
