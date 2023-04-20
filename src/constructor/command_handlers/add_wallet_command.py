import json

from src.database.chat_state import update_chat_state
from src.constructor.bot_response import respond_with_text


def handler(data, chat_state):
    chat_id = data["message"]["chat"]["id"]
    command_state = {
        "active_command": "addWallet",
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }

    chat_state.update(command_state)
    update_chat_state(chat_state)

    respond_with_text("Please enter you Metamask wallet address!", chat_id)
