from src.database.routes import get_route_by_id, update_route, put_passenger_route, passenger_route_exists
from src.constructor.services.tg_keyboard import handle_navigation_buttons, handle_route_info_button
from src.constructor.bot_response import respond_with_text
from src.constructor.payment_handlers.payment_utils import deposit_to_contract


def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query['data']
    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(keyboard_id, callback_query, chat_state)
        return

    username = callback_query["from"]["username"]
    chat_id = callback_query["from"]["id"]

    route_id = callback_query['data']

    if button_info.startswith("info"):
        route = get_route_by_id(button_info.split("+")[-1])
        handle_route_info_button(route, chat_id)
        return

    route = get_route_by_id(route_id)

    is_passenger, error_message = validate_driver_against_route(chat_id, route)

    if not is_passenger:
        respond_with_text(error_message, chat_id)
        return

    can_join, error_message = validate_user_against_route(username, chat_id, route)

    if not can_join:
        respond_with_text(error_message, chat_id)
        return

    try:
        deposit_to_contract(
            username=username,
            amount=route["pricePerPerson"],
            chat_id=chat_id,
            additional_information={
                "route_id": route_id,
                "username": username,
                "chat_id": chat_id,
            }
        )
    except:
        respond_with_text("Could not withdraw the amount from the registered wallet", chat_id)


def validate_driver_against_route(route, chat_id):
    if chat_id == route["owner_chat_id"]:
        return False, "You cannot join you own ride.."


def validate_user_against_route(username, chat_id, route):
    max_capacity = route["maxPassengerCapacity"]
    current_passenger_count = route["joined_users_count"]
    if current_passenger_count >= max_capacity:
        return False, "Unfortunately, this route has reached its maximum passenger capacity"

    already_joined = passenger_route_exists(username, route['route_id'])
    if already_joined:
        return False, "User has already joined this route previously"

    return True, ""
