
from src.database.routes import delete_user_route, get_route_by_id_and_username
from src.constructor.services.tg_keyboard import handle_navigation_buttons


def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query['data']
    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(keyboard_id, callback_query, chat_state)
        return

    username = callback_query["from"]["username"]
    route_id = callback_query['data']
    route = get_route_by_id_and_username(route_id, username)
    delete_user_route(route["pk"], route["sk"])
