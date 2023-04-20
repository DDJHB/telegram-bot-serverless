import json

from src.constructor.bot_response import respond_with_text
from src.database.chat_state import update_chat_state


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]

    command_state = {
        "active_command": "searchRoutes",
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }

    chat_state.update(command_state)
    update_chat_state(chat_state)

    respond_with_text("Please share the starting location! Use Telegram built-in 'share location' attachment!", chat_id)
