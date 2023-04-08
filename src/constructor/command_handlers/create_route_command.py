import json
from src.database.chat_state import put_chat_state


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    command_state = {
        "active_command": "createRoute",
        "current_step_index": 0,
        "command_info": json.dumps({}),
        "login_timestamp": chat_state['login_timestamp'],
    }

    put_chat_state(chat_id, command_state)

    return "Please share the starting location! Use Telegram built-in 'share location' attachment."
