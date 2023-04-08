import json
import web3.exceptions
from web3 import Web3
import re

from src.constructor.web3_utils import get_base_wallet_info, send_transaction_to_contract, call_view_contract_method
from src.database.chat_state import update_chat_state
from src.database.eth_transactions import put_transaction_request

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


def step_handler(data, state_record):
    prev_step_index = int(state_record['current_step_index'])

    try:
        update_command_info = handle_prev_step_data(data, prev_step_index)
    except UserDataInvalid as error:
        return "Please, adhere to the format provided!"

    old_command_info = json.loads(state_record['command_info'])
    new_command_info = old_command_info | update_command_info
    state_record["command_info"] = json.dumps(new_command_info)

    if prev_step_index == 0:
        if not check_password(username=data["message"]["chat"]["username"],
                              password=state_record['command_info']['oldPassword']):
            return "User password is not correct."

    else:
        update_user(
            username=data["message"]["chat"]["username"],
            password=state_record['command_info']['newPassword'],
            chat_id=data["message"]["chat"]["id"],
        )
        state_record["active_command"] = None

    state_record["current_step_index"] = prev_step_index + 1
    update_chat_state(state_record)

    step_name = update_sequence[prev_step_index]
    return step_conf[step_name]["bot_response_message"]


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
    function_args = {
        "username": username,
        "password": Web3.keccak(text=password),
    }
    wallet_info = get_base_wallet_info()

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
            "function_args": json.dumps(function_args),
        }
    )
