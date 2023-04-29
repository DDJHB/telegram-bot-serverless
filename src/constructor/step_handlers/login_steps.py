import enum
import time
from decimal import Decimal

import web3.exceptions
from web3 import Web3

from src.constructor.web3_utils import call_view_contract_method
from src.constructor.bot_response import respond_with_text
from src.constructor.step_handlers.register_steps import validate_password
from src.database.chat_state import update_chat_state


def step_handler(data, chat_state):
    chat_id = chat_state["chat_id"]
    username = chat_state["username"]

    try:
        user_password = data["message"]['text']
    except KeyError:
        respond_with_text("Please, enter your password as a raw text!", chat_id)
        return

    if not validate_password(user_password, {}):
        respond_with_text("Please, adhere to the password format", chat_id)
        return

    response, response_message = login_user(username=username, password=user_password)

    respond_with_text(response_message, chat_id)

    if response != LoginResponses.CorrectCredentials:
        return

    chat_state.update({
        "active_command": None,
        'login_timestamp': Decimal(time.time())
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
