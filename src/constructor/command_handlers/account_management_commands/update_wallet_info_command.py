import os
import json
from src.database.chat_state import update_chat_state


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    command_state = {
        "active_command": "updateWalletInfo",
        "current_step_index": 0,
        "command_info": json.dumps({}),
        "login_timestamp": chat_state['login_timestamp'],
    }

    chat_state.update(command_state)
    update_chat_state(chat_state)

    return "Please enter new Metamask wallet address!"
