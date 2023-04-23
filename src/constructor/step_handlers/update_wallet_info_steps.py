import json
from web3 import Web3, Account

from src.database.chat_state import update_chat_state
from src.database.user_info import put_wallet_info_record
from src.constructor.bot_response import respond_with_text


update_sequence = [
    "newWalletAddress", "newPrivateKey",
]

step_conf = {
    "newWalletAddress": {
        "bot_response_message": "Enter Metamask wallet private key!"
    },
    "newPrivateKey": {
        "bot_response_message": "Wallet information has been updated!"
    },
}


def step_handler(data, chat_state):
    chat_id = chat_state["chat_id"]
    prev_step_index = int(chat_state['current_step_index'])

    try:
        update_command_info = handle_prev_step_data(data, prev_step_index, chat_state)
    except UserDataInvalid as error:
        respond_with_text("Please, adhere to the format provided!", chat_id)
        return

    old_command_info = json.loads(chat_state['command_info'])
    new_command_info = old_command_info | update_command_info
    chat_state["command_info"] = json.dumps(new_command_info)

    if prev_step_index == len(update_sequence) - 1:
        put_wallet_info_record(
            username=data["message"]["chat"]["username"],
            wallet_address=json.loads(chat_state['command_info'])['newWalletAddress'],
            private_key=json.loads(chat_state['command_info'])['newPrivateKey'],
            extra_fields={}
        )
        chat_state["active_command"] = None

    chat_state["current_step_index"] = prev_step_index + 1
    update_chat_state(chat_state)

    step_name = update_sequence[prev_step_index]
    respond_with_text(step_conf[step_name]["bot_response_message"], chat_id)


def handle_prev_step_data(data: dict, prev_step_index: int, chat_state: dict) -> dict:
    key = update_sequence[prev_step_index]
    validator_by_key = {
        "newWalletAddress": validate_wallet_address,
        "newPrivateKey": validate_private_key,
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


class UserDataInvalid(Exception):
    ...


def validate_wallet_address(wallet_address, chat_state):
    return Web3.isAddress(wallet_address)


def validate_private_key(private_key, chat_state):
    wallet_address = json.loads(chat_state.get("command_info", '{}')).get("walletAddress")
    account = Account.privateKeyToAccount(private_key)
    return account.address.lower() == wallet_address.lower()
