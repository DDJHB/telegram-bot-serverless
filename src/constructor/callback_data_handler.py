import json

from src.database.chat_state import get_chat_state
from src.constructor.keyboard_handlers import (
    routes_keyboard,
)

data_handler_by_keyboard = {
    "routes_keyboard": routes_keyboard.handler,
}


def handle_callback_data(data: dict, chat_state: dict) -> str:
    keyboard_id = str(data['callback_query']["message"]["message_id"])
    keyboard_info = json.loads(chat_state["global_keyboards_info"])[keyboard_id]

    if handler := data_handler_by_keyboard[keyboard_info["keyboard_name"]]:
        response = handler(keyboard_id, data["callback_query"], chat_state)

    else:
        response = ""

    return response
