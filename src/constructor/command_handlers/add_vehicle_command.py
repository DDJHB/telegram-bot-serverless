import json

from src.database.chat_state import update_chat_state
from src.constructor.bot_response import respond_with_text
from src.constructor.services.vehicle_crud import get_user_vehicles

def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']

    number_of_vehicles = len(get_user_vehicles(username))
    if number_of_vehicles >= 5:
        respond_with_text("You have reached maximum number of vehicles registered! Please, delete at least one to "
                          "proceed", chat_id)
        return

    command_state = {
        "active_command": "addVehicle",
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }

    chat_state.update(command_state)
    update_chat_state(chat_state)

    respond_with_text("Please provide your license plate number!", chat_id)
