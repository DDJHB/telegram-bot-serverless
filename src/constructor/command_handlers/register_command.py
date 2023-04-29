import json

import web3.exceptions
from web3 import Web3

from src.constructor.web3_utils import call_view_contract_method
from src.database.chat_state import update_chat_state
from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data["message"]["chat"]["username"]

    if is_registered(username):
        respond_with_text("You are already registered! Please, log in to continue.", chat_id)
        return

    command_state = {
        "active_command": "register",
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }

    chat_state.update(command_state)

    update_chat_state(chat_state)

    respond_with_text("Please create password!\n"
                      "Password must be between 8 and 24 characters in length.\n"
                      "Password must include both upper-case and lower-case letters, and a number", chat_id)


def is_registered(username):
    response = call_view_contract_method(
        contract_name="onboarding",
        function_name="isRegistered",
        function_args=[username]
    )

    return response
