import json
from src.database.chat_state import put_chat_state


def handler(data):
    chat_id = data["message"]["chat"]["id"]
    command_state = {
        "active_command": "createRoute",
        "current_step_index": 0,
        "command_info": json.dumps({})
    }

    put_chat_state(chat_id, command_state)

    return "Please share the starting location! Use Telegram built-in 'share location' attachment."
