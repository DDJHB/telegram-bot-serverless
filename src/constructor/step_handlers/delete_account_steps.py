import json
import web3.exceptions
from web3 import Web3

from src.constructor.services.vehicle_crud import remove_user_vehicles
from src.constructor.web3_utils import send_transaction_to_contract, call_view_contract_method
from src.database.chat_state import update_chat_state
from src.database.eth_transactions import put_transaction_request
from src.constructor.bot_response import respond_with_text
from src.database.user_info import get_user_info_record, delete_user_info_record

update_sequence = [
    "password",
]

step_conf = {
    "password": {
        "bot_response_message": "Deleting account information..."
    }
}


def step_handler(data, chat_state):
    chat_id = chat_state["chat_id"]
    prev_step_index = int(chat_state['current_step_index'])

    try:
        update_command_info = handle_prev_step_data(data, prev_step_index)
    except UserDataInvalid as error:
        respond_with_text("User password is not correct.", chat_id)
        return

    old_command_info = json.loads(chat_state['command_info'])
    new_command_info = old_command_info | update_command_info
    chat_state["command_info"] = json.dumps(new_command_info)

    remove_user_vehicles(
        username=data["message"]["chat"]["username"],
        chat_id=data["message"]["chat"]["id"]
    )

    delete_user(
        username=data["message"]["chat"]["username"],
        chat_id=data["message"]["chat"]["id"],
    )

    delete_user_info_record(username=data["message"]["chat"]["username"])

    chat_state["active_command"] = None

    chat_state["current_step_index"] = prev_step_index + 1
    update_chat_state(chat_state)

    step_name = update_sequence[prev_step_index]
    respond_with_text(step_conf[step_name]["bot_response_message"], chat_id)


def handle_prev_step_data(data: dict, prev_step_index: int) -> dict:
    key = update_sequence[prev_step_index]
    validator_by_key = {
        "password": check_password
    }
    key_validator = validator_by_key[key]
    try:
        is_valid = key_validator(data["message"]["from"]["username"], data["message"]["text"])
        if not is_valid:
            raise UserDataInvalid
    except KeyError as error:
        raise UserDataInvalid

    update_command_info = {
        key: data["message"]['text']
    }
    return update_command_info


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


def delete_user(username: str, chat_id: int):
    function_name = "deleteAccount"
    contract_name = "onboarding"

    wallet_info = get_user_info_record(username)

    tx_hash = send_transaction_to_contract(
        wallet_info=wallet_info,
        contract_name=contract_name,
        function_name=function_name,
        function_args=[username],
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
