import json

from src.constructor.services.vehicle_crud import get_user_vehicles
from src.database.chat_state import update_chat_state
from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']

    vehicles = get_user_vehicles(username)
    if len(vehicles) == 0:
        respond_with_text("You have no registered vehicles!", chat_id)
        return

    command_state = {
        "active_command": "createRoute",
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }

    chat_state.update(command_state)
    update_chat_state(chat_state)

    respond_with_text("Please name your ride!", chat_id)
