import json

from src.database.routes import get_passengers_routes_by_route_id, get_route_by_id, update_route
from src.database.chat_state import update_chat_state, get_chat_state
from src.constructor.services.tg_keyboard import handle_navigation_buttons
from src.constructor.bot_response import respond_with_inline_keyboard, respond_with_text
from src.constructor.services.tg_keyboard import build_approval_keyboard


def handler(keyboard_id, callback_query, chat_state):
    button_info = callback_query['data']  # route_id
    if any(button_info.startswith(button_name) for button_name in ["next", "back"]):
        handle_navigation_buttons(keyboard_id, callback_query, chat_state)
        return

    route = get_route_by_id(button_info)

    if route["has_started"]:
        respond_with_text("This ride has already started!", callback_query['message']['chat']['id'])
        return

    route.update({
        "has_started": False,
        "approval_info": {
            "YES": 0,
            "NO": 0,
        }
    })
    route['approval_info'] = json.dumps(route['approval_info'])
    update_route(route)

    passenger_routes = get_passengers_routes_by_route_id(button_info)['Items']

    passenger_chat_ids = [item["chat_id"] for item in passenger_routes]

    keyboard_def = build_approval_keyboard(route)

    for chat_id in passenger_chat_ids:
        tg_response = respond_with_inline_keyboard(
            parent_message=f"Please select if the route {button_info} has started: ",
            keyboard_definition=keyboard_def,
            chat_id=chat_id,
        )

        keyboard_id = str(tg_response.json()['result']["message_id"])
        passenger_chat_state = get_chat_state(chat_id)
        global_keyboards_info = json.loads(passenger_chat_state.get("global_keyboards_info") or '{}')
        global_keyboards_info.update(
            {
                keyboard_id: {
                    "keyboard_name": "approve_start_route_keyboard",
                }
            }
        )

        passenger_chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
        update_chat_state(passenger_chat_state)
