from src.database.routes import get_route_by_id_and_username, update_route
from src.constructor.services.tg_keyboard import handle_navigation_buttons


def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query['data']
    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(keyboard_id, callback_query, chat_state)
        return

    # none of the shit below will work

    username = callback_query["from"]["username"]
    route_id = callback_query['data']
    route = get_route_by_id_and_username(route_id, username)

    # 1. add new route to DB for passenger

    route["joined_users_count"] = route["joined_users_count"] + 1

    route.update({"joined_users_count": route["joined_users_count"] + 1})
    update_route(route)
