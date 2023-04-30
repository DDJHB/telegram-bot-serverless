import json

from src.constructor.keyboard_handlers import (
    delete_vehicle_keyboard, routes_keyboard,
    delete_route_keyboard, select_route_vehicle_keyboard,
    start_route_keyboard, approve_start_route_keyboard,
    join_route_keyboard, rate_driver_keyboard,
    end_route_keyboard, approve_end_route_keyboard,
    joined_routes_keyboard,
)

keyboard_by_name = {
    "routes_keyboard": routes_keyboard,
    "joined_routes_keyboard": joined_routes_keyboard,
    "delete_route_keyboard": delete_route_keyboard,
    "delete_vehicle_keyboard": delete_vehicle_keyboard,
    "start_route_keyboard": start_route_keyboard,
    "approve_start_route_keyboard": approve_start_route_keyboard,
    "end_route_keyboard": end_route_keyboard,
    "approve_end_route_keyboard": approve_end_route_keyboard,
    "join_route_keyboard": join_route_keyboard,
    "rate_driver_keyboard": rate_driver_keyboard,
    "select_route_vehicle_keyboard": select_route_vehicle_keyboard,
}


def handle_callback_data(data: dict, chat_state: dict) -> str:
    keyboard_id = str(data['callback_query']["message"]["message_id"])
    keyboard_info = json.loads(chat_state.get("global_keyboards_info", {})).get(keyboard_id)
    response = None

    if keyboard := keyboard_by_name[keyboard_info.get("keyboard_name")]:
        response = keyboard.handler(keyboard_id, data["callback_query"], chat_state)

    return response
