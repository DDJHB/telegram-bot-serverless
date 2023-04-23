from src.database.routes import get_route_by_id, update_route, put_passenger_route, passenger_route_exists
from src.constructor.services.tg_keyboard import handle_navigation_buttons
from src.constructor.bot_response import respond_with_text


def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query['data']
    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(keyboard_id, callback_query, chat_state)
        return

    username = callback_query["from"]["username"]
    chat_id = callback_query["from"]["id"]

    route_id = callback_query['data']

    route = get_route_by_id(route_id)

    can_join, error_message = validate_user_against_route(username, chat_id, route)

    if not can_join:
        respond_with_text(error_message, chat_id)
        return

    route.update({"joined_users_count": route["joined_users_count"] + 1})
    update_route(route)

    put_passenger_route(
        driver_route=route,
        username=username,
        chat_id=chat_id,
    )

    # TODO add money withdrawal
    respond_with_text(f"Successfully joined route {route.get('route_name', 'random')}", chat_id)


def validate_user_against_route(username, chat_id, route):
    max_capacity = route["maxPassengerCapacity"]
    current_passenger_count = route["joined_users_count"]
    if current_passenger_count >= max_capacity:
        return False, "Unfortunately, this route has reached its maximum passenger capacity"

    already_joined = passenger_route_exists(username, route['route_id'])
    if already_joined:
        return False, "User has already joined this route previously"

    return True, ""
