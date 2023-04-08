import os
import json
from src.database.chat_state import put_chat_state


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    command_state = {
        "active_command": "register",
        "current_step_index": 0,
        "command_info": json.dumps({})
    }

    put_chat_state(chat_id, command_state)

    return "Please create password!"

