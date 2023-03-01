from http import HTTPStatus

import requests

from src.constructor.decorators import standard_api_handler
from src.constructor.bot_response import respond_with_text
from src.constructor.command_handler import handle_command


@standard_api_handler
def greet(event, context):
    try:
        data = event["body"]
        message = str(data["message"]["text"])
        chat_id = data["message"]["chat"]["id"]

        if message.startswith('/'):
            response = handle_command(data)
        else:
            # TODO: remove
            response = 'Please, wait for the alpha launch of the bot...'

        respond_with_text(response, chat_id)

        return {'statusCode': HTTPStatus.OK}
    except Exception as e:
        print(e)
        requests.post(
            url="https://eow4z7ghug68ys0.m.pipedream.net",
            data=e
        )
        return {'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR, 'body': {"message": "Internal Server Error"}}
