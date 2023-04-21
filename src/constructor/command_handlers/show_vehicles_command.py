import json

from src.database.chat_state import update_chat_state
from src.constructor.services.vehicle_crud import get_user_vehicles
from src.constructor.bot_response import respond_with_text
from src.constructor.services.tg_keyboard import build_view_keyboard


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']

    vehicles = get_user_vehicles(username)

    response = ""
    for ind, vehicle in enumerate(vehicles):
        response += f"{ind+1}. {vehicle[0]}, {vehicle[1]}, {vehicle[2]}, {vehicle[3]}\n"

    respond_with_text(response, chat_id)
