import time
import enum
import decimal

import web3.exceptions
from web3 import Web3

from src.constructor.web3_utils import call_view_contract_method
from src.database.chat_state import update_chat_state
from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    username = data["message"]["chat"]["username"]
    message = str(data["message"]["text"])
    if " " not in message:
        respond_with_text(f"Please enter the password with /login xxxx command!", chat_state["chat_id"])

    user_password = message.split(" ")[1]
    response, response_message = login_user(username=username, password=user_password)

    respond_with_text(response_message, chat_state["chat_id"])

    if response != LoginResponses.CorrectCredentials:
        return

    chat_state.update({
        'login_timestamp': decimal.Decimal(time.time())
    })
    update_chat_state(chat_state)


def login_user(username, password):
    try:
        response = call_view_contract_method(
            contract_name="onboarding",
            function_name="login",
            function_args=[username, Web3.keccak(text=password)]
        )
        print(response)
    except web3.exceptions.ContractLogicError as error:
        print(error)
        return LoginResponses.InvalidPassword, "User is not registered/password is not correct"

    return LoginResponses.CorrectCredentials, "User has been signed in..."


class LoginResponses(enum.IntEnum):
    UserNotRegistered = enum.auto()
    InvalidPassword = enum.auto()
    CorrectCredentials = enum.auto()
