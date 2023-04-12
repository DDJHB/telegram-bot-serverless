import json
from web3 import Web3, Account
import re

from src.constructor.web3_utils import get_base_wallet_info, send_transaction_to_contract
from src.database.chat_state import update_chat_state
from src.database.eth_transactions import put_transaction_request
from src.database.user_info import put_wallet_info_record

wallet_info_sequence = [
    "walletAddress", "privateKey",
]

step_conf = {
    "walletAddress": {
        "bot_response_message": "Please enter your Metamask wallet private key!"
    },
    "privateKey": {
        "bot_response_message": "Your wallet information has been saved!"
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

    if prev_step_index == len(wallet_info_sequence) - 1:
        state_record["active_command"] = None
        update_chat_state(state_record)
        put_wallet_info_record(
            username=data["message"]["chat"]["username"],
            wallet_address=state_record['command_info']['wallet_address'],
            private_key=state_record['command_info']['private_key'],
        )
        step_name = wallet_info_sequence[prev_step_index]
        return step_conf[step_name]["bot_response_message"]

    state_record["current_step_index"] = prev_step_index + 1
    update_chat_state(state_record)

    step_name = wallet_info_sequence[prev_step_index]
    return step_conf[step_name]["bot_response_message"]


def handle_prev_step_data(data: dict, prev_step_index: int) -> dict:
    key = wallet_info_sequence[prev_step_index]
    validator_by_key = {
        "walletAddress": validate_wallet_address,
        "privateKey": validate_private_key,
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


def validate_wallet_address(wallet_address):
    return Web3.isAddress(wallet_address)


def validate_private_key(private_key, wallet_address):
    account = Account.privateKeyToAccount(private_key)
    return account.address.lower() == wallet_address.lower()


class UserDataInvalid(Exception):
    ...

