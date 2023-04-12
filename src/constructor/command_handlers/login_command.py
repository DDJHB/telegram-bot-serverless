import time

import web3.exceptions
from web3 import Web3

from src.constructor.web3_utils import call_view_contract_method
from src.database.chat_state import update_chat_state


def handler(data: dict, chat_state: dict):
    username = data["message"]["chat"]["username"]
    message = str(data["message"]["text"])
    if " " not in message:
        return f"Please enter the password with /login xxxx command!"

    user_password = message.split(" ")[1]
    response = login_user(username=username, password=user_password)
    chat_state.update({
        'login_timestamp': time.time()
    })
    update_chat_state(chat_state)
    return response


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
        return "User is not registered/password is not correct"

    # respond to user
    return "User has been signed in..."
