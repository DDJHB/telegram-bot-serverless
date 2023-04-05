from http import HTTPStatus
import traceback

import requests

from src.constructor.decorators import standard_api_handler
from src.constructor.bot_response import respond_with_text

from src.constructor.command_handler import handle_command
from src.constructor.step_handler import handle_step
from src.constructor.callback_data_handler import handle_callback_data


@standard_api_handler
def handler(event, context):
    try:
        data = event["body"]
        print(data)
        if data.get("callback_query"):
            response = handle_callback_data(data)
        elif text := data["message"].get("text"):
            text = str(text)
            if text.startswith('/'):
                response = handle_command(data)
            else:
                response = handle_step(data)
        else:
            response = handle_step(data)

        chat_id = data["message"]["chat"]["id"]
        respond_with_text(response, chat_id)

        return {'statusCode': HTTPStatus.OK}
    except Exception as e:
        print(traceback.format_exc())
        requests.post(
            url="https://eow4z7ghug68ys0.m.pipedream.net",
            data=repr(e)
        )
        return {'statusCode': 200, 'body': {"message": "received ur message chill"}}
