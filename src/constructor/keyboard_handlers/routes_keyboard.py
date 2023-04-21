
from src.constructor.services.tg_keyboard import handle_navigation_buttons


def handler(keyboard_id, callback_query, chat_state):
    handle_navigation_buttons(keyboard_id, callback_query, chat_state)