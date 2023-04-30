import json
from src.database.routes import get_route_by_id, passenger_route_exists
from src.database.chat_state import update_chat_state
from src.constructor.services.tg_keyboard import handle_route_info_button
from src.constructor.bot_response import respond_with_text, delete_message
from src.constructor.payment_handlers.payment_utils import deposit_to_contract
from src.constructor.services.route import compute_routes
from src.constructor.services.tg_keyboard import (
    extend_keyboard_with_route_id_buttons, build_view_keyboard, update_inline_keyboard
)
from src.database.routes import update_route, put_passenger_route

def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query['data']
    chat_id = callback_query["from"]["id"]

    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(
            button_name=button_info,
            chat_state=chat_state,
            chat_id=chat_id,
            keyboard_id=keyboard_id,
        )
        return

    username = callback_query["from"]["username"]

    route_id = callback_query['data']

    if button_info.startswith("info"):
        route = get_route_by_id(button_info.split("+")[-1])
        handle_route_info_button(route, chat_id)
        return

    route = get_route_by_id(route_id)

    is_passenger, error_message = validate_driver_against_route(route, chat_id)

    if not is_passenger:
        respond_with_text(error_message, chat_id)
        return

    can_join, error_message = validate_user_against_route(username, chat_id, route)

    if not can_join:
        respond_with_text(error_message, chat_id)
        return

    try:
        # deposit_to_contract( TODO move back
        #     username=username,
        #     amount=route["pricePerPerson"],
        #     chat_id=chat_id,
        #     additional_information={
        #         "route_id": route_id,
        #         "username": username,
        #         "chat_id": chat_id,
        #     }
        # )
        route.update({"joined_users_count": route["joined_users_count"] + 1})
        update_route(route)

        put_passenger_route(
            driver_route=route,
            username=username,
            chat_id=chat_id,
        )

        delete_message(chat_id, keyboard_id)
        respond_with_text(f"Successfully joined route {route.get('route_name', 'random')}", chat_id)
    except:
        respond_with_text("Could not withdraw the amount from the registered wallet", chat_id)


def validate_driver_against_route(route, chat_id):
    if chat_id == route["owner_chat_id"]:
        return False, "You cannot join you own ride.."

    return True, ""


def validate_user_against_route(username, chat_id, route):
    max_capacity = route["maxPassengerCapacity"]
    current_passenger_count = route["joined_users_count"]
    if current_passenger_count >= max_capacity:
        return False, "Unfortunately, this route has reached its maximum passenger capacity"

    already_joined = passenger_route_exists(username, route['route_id'])
    if already_joined:
        return False, "User has already joined this route previously"

    return True, ""


def handle_navigation_buttons(*, button_name, chat_state, chat_id, keyboard_id):
    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    keyboard_info = global_keyboards_info[keyboard_id]

    page_info = keyboard_info["page_info"]
    current_page_number = page_info["current_page_number"]
    search_route_info = keyboard_info["search_info"]

    if button_name == "next":
        last_evaluated_key = page_info["last_evaluated_keys"][str(current_page_number)]
        response = compute_routes(search_route_info, last_key=last_evaluated_key)
        routes = response.get("Items", [])
        if not routes:
            response = compute_routes(search_route_info, last_key=None)
            routes = response.get("Items", [])
        keyboard_definition = extend_keyboard_with_route_id_buttons(build_view_keyboard(routes), routes)
        update_inline_keyboard(chat_id, keyboard_id, keyboard_definition)

        new_last_evaluated_key = response.get('LastEvaluatedKey')
        new_page_number = current_page_number + 1

        page_info["last_evaluated_keys"][str(new_page_number)] = new_last_evaluated_key
        page_info["current_page_number"] = new_page_number
        global_keyboards_info[keyboard_id].update({"page_info": page_info})

        chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
        update_chat_state(chat_state)
    else:
        if current_page_number == 1:
            return

        needed_page_number = current_page_number - 2
        needed_page_le_key = page_info["last_evaluated_keys"].get(str(needed_page_number))
        response = compute_routes(search_route_info, last_key=needed_page_le_key)
        items = response['Items']

        keyboard_definition = extend_keyboard_with_route_id_buttons(build_view_keyboard(items), items)
        update_inline_keyboard(chat_id, keyboard_id, keyboard_definition)

        new_last_evaluated_key = response.get('LastEvaluatedKey')
        new_page_number = current_page_number - 1

        page_info["last_evaluated_keys"][str(new_page_number)] = new_last_evaluated_key
        page_info["current_page_number"] = new_page_number
        global_keyboards_info[keyboard_id].update({"page_info": page_info})

        chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
        update_chat_state(chat_state)
