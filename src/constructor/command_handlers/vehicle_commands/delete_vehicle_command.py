import json

from src.constructor.bot_response import respond_with_text, respond_with_inline_keyboard
from src.constructor.services.tg_keyboard import build_indexed_keyboard
from src.database.chat_state import update_chat_state
from src.constructor.services.vehicle_crud import get_user_vehicles


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']

    vehicles = get_user_vehicles(username)
    if len(vehicles) == 0:
        respond_with_text("You have no registered vehicles!", chat_id)
        return

    respond_with_text("Select a vehicle you want to remove:", chat_id)

    licenses = [v[0] for v in vehicles]
    if not licenses:
        respond_with_text("You do not have any vehicles registered!", chat_id)
        return
    keyboard_def = build_indexed_keyboard(licenses)
    tg_response = respond_with_inline_keyboard(
        parent_message="Your vehicles:",
        keyboard_definition=keyboard_def,
        chat_id=chat_id,
    )

    keyboard_id = str(tg_response.json()['result']["message_id"])
    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    global_keyboards_info.update(
        {
            keyboard_id: {
                "keyboard_name": "delete_vehicle_keyboard",
            }
        }
    )

    chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})

    command_state = {
        "active_command": "deleteVehicle",
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }
    chat_state.update(command_state)

    update_chat_state(chat_state)
