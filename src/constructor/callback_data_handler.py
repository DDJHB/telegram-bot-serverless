import json

from src.constructor.keyboard_handlers import (
    routes_keyboard, delete_route_keyboard, delete_vehicle_keyboard,
)

keyboard_by_name = {
    "routes_keyboard": routes_keyboard,
    "delete_route_keyboard": delete_route_keyboard,
    "delete_vehicle_keyboard": delete_vehicle_keyboard,
}


def handle_callback_data(data: dict, chat_state: dict) -> str:
    keyboard_id = str(data['callback_query']["message"]["message_id"])
    keyboard_info = json.loads(chat_state["global_keyboards_info"])[keyboard_id]

    response = None

    if keyboard := keyboard_by_name[keyboard_info["keyboard_name"]]:
        response = keyboard.handler(keyboard_id, data["callback_query"], chat_state)

    return response
