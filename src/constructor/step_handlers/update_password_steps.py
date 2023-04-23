import json
import web3.exceptions
from web3 import Web3
import re

from src.constructor.web3_utils import send_transaction_to_contract, call_view_contract_method
from src.database.chat_state import update_chat_state
from src.database.eth_transactions import put_transaction_request
from src.constructor.bot_response import respond_with_text
from src.database.user_info import get_user_info_record

update_sequence = [
    "oldPassword", "newPassword",
]

step_conf = {
    "oldPassword": {
        "bot_response_message": "Enter new password!"
    },
    "newPassword": {
        "bot_response_message": "Updating user information..."
    },
}


def step_handler(data, chat_state):
    chat_id = chat_state["chat_id"]
    prev_step_index = int(chat_state['current_step_index'])

    try:
        update_command_info = handle_prev_step_data(data, prev_step_index)
    except UserDataInvalid as error:
        respond_with_text("Please, adhere to the format provided!", chat_id)
        return

    old_command_info = json.loads(chat_state['command_info'])
    new_command_info = old_command_info | update_command_info
    chat_state["command_info"] = json.dumps(new_command_info)

    if prev_step_index == 0:
        if not check_password(
            username=data["message"]["chat"]["username"],
            password=json.loads(chat_state['command_info'])['oldPassword']
        ):
            respond_with_text("User password is not correct.", chat_id)
            return

    else:
        update_user(
            username=data["message"]["chat"]["username"],
            password=json.loads(chat_state['command_info'])['newPassword'],
            chat_id=data["message"]["chat"]["id"],
        )
        chat_state["active_command"] = None

    chat_state["current_step_index"] = prev_step_index + 1
    update_chat_state(chat_state)

    step_name = update_sequence[prev_step_index]
    respond_with_text(step_conf[step_name]["bot_response_message"], chat_id)


def handle_prev_step_data(data: dict, prev_step_index: int) -> dict:
    key = update_sequence[prev_step_index]
    validator_by_key = {
        "oldPassword": do_not_validate,
        "newPassword": validate_password,
    }
    key_validator = validator_by_key[key]
    try:
        is_valid = key_validator(data["message"]['text'])
        if not is_valid:
            raise UserDataInvalid
    except KeyError as error:
        raise UserDataInvalid

    update_command_info = {
        key: data["message"]['text']
    }
    return update_command_info


def do_not_validate(dummy) -> True:
    return True


def validate_password(password: str):
    if len(password) < 8 or len(password) > 24:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


class UserDataInvalid(Exception):
    ...


def check_password(username: str, password: str):
    try:
        response = call_view_contract_method(
            contract_name="onboarding",
            function_name="login",
            function_args=[username, Web3.keccak(text=password)]
        )
        print(response)
    except web3.exceptions.ContractLogicError as error:
        print(error)
        return False

    return True


def update_user(username: str, password: str, chat_id: int):
    function_name = "updatePassword"
    contract_name = "onboarding"

    wallet_info = get_user_info_record(username)

    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[username, Web3.keccak(text=password)],
    )

    # save to db
    put_transaction_request(
        tx_hash=tx_hash,
        chat_id=chat_id,
        extra_fields={
            "username": username,
            "function_name": function_name,
            "contract_name": contract_name,
            "function_args": json.dumps({}),
        }
    )
