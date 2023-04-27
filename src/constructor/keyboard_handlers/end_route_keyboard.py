import json

from src.database.routes import get_passengers_routes_by_route_id, get_route_by_id
from src.database.chat_state import update_chat_state, get_chat_state
from src.constructor.services.tg_keyboard import handle_navigation_buttons
from src.constructor.bot_response import respond_with_inline_keyboard
from src.constructor.services.tg_keyboard import build_approval_keyboard


def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query['data']  # route_id
    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(keyboard_id, callback_query, chat_state)
        return

    check_route_start(button_info)

    passenger_routes = get_passengers_routes_by_route_id(button_info)['Items']

    passenger_chat_ids = [item["passenger_chat_id"] for item in passenger_routes]

    keyboard_def = build_approval_keyboard(button_info)

    for chat_id in passenger_chat_ids:
        tg_response = respond_with_inline_keyboard(
            parent_message="Please select if the route has ended:",
            keyboard_definition=keyboard_def,
            chat_id=chat_id,
        )

        keyboard_id = str(tg_response.json()['result']["message_id"])
        passenger_chat_state = get_chat_state(chat_id)
        global_keyboards_info = json.loads(passenger_chat_state.get("global_keyboards_info") or '{}')
        global_keyboards_info.update(
            {
                keyboard_id: {
                    "keyboard_name": "approve_end_route_keyboard",
                    "page_info": {
                        "last_evaluated_keys": None,
                        "current_page_number": None,
                    },
                }
            }
        )

        passenger_chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
        update_chat_state(passenger_chat_state)


def check_route_start(route_id: str):
    route = get_route_by_id(route_id)
    if not route["has_started"]:
        return False
    return True
