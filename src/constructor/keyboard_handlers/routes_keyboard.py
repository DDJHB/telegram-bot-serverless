
from src.constructor.services.tg_keyboard import handle_navigation_buttons, handle_route_info_button
from src.database.routes import get_route_by_id


def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query["data"]
    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(keyboard_id, callback_query, chat_state)
        return

    _, route_id = button_info.split("+")
    route = get_route_by_id(route_id)
    chat_id = callback_query["from"]["id"]
    handle_route_info_button(route, chat_id)
