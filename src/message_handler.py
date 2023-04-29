import time
from http import HTTPStatus
import traceback
import enum
import decimal

import requests

from src.constructor.decorators import standard_api_handler
from src.constructor.bot_response import respond_with_text

from src.constructor.command_handler import handle_command
from src.constructor.step_handler import handle_step
from src.constructor.callback_data_handler import handle_callback_data
from src.database.chat_state import get_chat_state, put_chat_state


@standard_api_handler
def handler(event, context):
    try:
        data = event["body"]
        print(data)
        chat_id, username = extract_chat_identifiers(data)

        chat_state = get_chat_state(chat_id)
        if not chat_state:
            chat_state = put_chat_state(
                chat_id,
                {
                    "username": username,
                    "login_timestamp": decimal.Decimal(1.0)
                }
            )

        error = handle_session_login(data, chat_state, chat_id)
        if error == UserMessageErrors.UserNotSignedIn:
            return {'statusCode': HTTPStatus.OK}

        if data.get("callback_query"):
            response = handle_callback_data(data, chat_state)
        elif text := data.get("message", {}).get("text"):
            text = str(text)
            if text.startswith('/'):
                response = handle_command(data, chat_state)
            else:
                response = handle_step(data, chat_state)
        else:
            response = handle_step(data, chat_state)

        if response:
            respond_with_text(response, chat_id)

        return {'statusCode': HTTPStatus.OK}
    except Exception as e:
        print(traceback.format_exc())
        requests.post(
            url="https://eow4z7ghug68ys0.m.pipedream.net",
            data=repr(e)
        )
        return {'statusCode': 200, 'body': {"message": "received ur message chill:)"}}


def extract_chat_identifiers(data):
    if callback_query := data.get("callback_query"):
        return callback_query["message"]['chat']["id"], callback_query["from"]["username"]
    else:
        return data["message"]["chat"]["id"], data["message"]["from"]["username"]


def handle_session_login(data, chat_state, chat_id):
    day_in_seconds = 1 * 24 * 60 * 60
    text = data.get("message", {}).get("text")
    if not text:
        return
    if is_login_command(text) or is_start_command(text) or is_register_command(text):
        return

    active_command = chat_state.get("active_command")
    if active_command in ("register", "login"):
        return

    if login_timestamp := chat_state.get("login_timestamp"):
        print(time.time() - float(login_timestamp))
        if time.time() - float(login_timestamp) > day_in_seconds:
            respond_with_text("Please log in to continue...", chat_id)
            return UserMessageErrors.UserNotSignedIn


def is_login_command(text):
    return text.startswith("/login")


def is_start_command(text):
    return text.startswith("/start")


def is_register_command(text):
    return text.startswith("/register")


class UserMessageErrors(enum.IntEnum):
    UserNotSignedIn = enum.auto()
