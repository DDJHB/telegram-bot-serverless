import json
from web3 import Web3, Account
import re

from src.constructor.web3_utils import get_base_wallet_info, send_transaction_to_contract
from src.database.chat_state import update_chat_state
from src.database.eth_transactions import put_transaction_request
from src.database.user_info import put_wallet_info_record, get_wallet_info_record

register_sequence = [
    "password", "walletAddress", "privateKey"
]

step_conf = {
    "password": {
        "bot_response_message": "Please enter you Metamask wallet address!"
    },
    "walletAddress": {
        "bot_response_message": "Please enter your Metamask wallet private key!"
    },
    "privateKey": {
        "bot_response_message": "Registering User..."
    },
}


def step_handler(data, state_record):
    prev_step_index = int(state_record['current_step_index'])

    try:
        update_command_info = handle_prev_step_data(data, prev_step_index, state_record)
    except UserDataInvalid as error:
        return "Please, adhere to the format provided!"

    old_command_info = json.loads(state_record['command_info'])
    new_command_info = old_command_info | update_command_info
    state_record["command_info"] = json.dumps(new_command_info)

    if prev_step_index == len(register_sequence) - 1:
        put_wallet_info_record(
            username=data["message"]["chat"]["username"],
            wallet_address=json.loads(state_record['command_info'])['walletAddress'],
            private_key=json.loads(state_record['command_info'])['privateKey'],
            extra_fields={}
        )
        register_user(
            username=data["message"]["chat"]["username"],
            password=json.loads(state_record['command_info'])['password'],
            chat_id=data["message"]["chat"]["id"],
        )

        state_record["active_command"] = None

    state_record["current_step_index"] = prev_step_index + 1
    update_chat_state(state_record)

    step_name = register_sequence[prev_step_index]
    return step_conf[step_name]["bot_response_message"]


def handle_prev_step_data(data: dict, prev_step_index: int, chat_state: dict) -> dict:
    key = register_sequence[prev_step_index]
    validator_by_key = {
        "password": validate_password,
        "walletAddress": validate_wallet_address,
        "privateKey": validate_private_key,
    }
    key_validator = validator_by_key[key]
    try:
        is_valid = key_validator(data["message"]['text'], chat_state)
        if not is_valid:
            raise UserDataInvalid
    except KeyError as error:
        raise UserDataInvalid

    update_command_info = {
        key: data["message"]['text']
    }
    return update_command_info


def validate_password(password: str, chat_state: dict):
    if len(password) < 8 or len(password) > 24:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def validate_wallet_address(wallet_address, chat_state):
    return Web3.isAddress(wallet_address)


def validate_private_key(private_key, chat_state):
    wallet_address = json.loads(chat_state.get("command_info", '{}')).get("walletAddress")
    account = Account.privateKeyToAccount(private_key)
    return account.address.lower() == wallet_address.lower()


class UserDataInvalid(Exception):
    ...


def register_user(username: str, password: str, chat_id: int):
    function_name = "registerUser"
    contract_name = "onboarding"

    wallet_info = get_wallet_info_record(username)

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
