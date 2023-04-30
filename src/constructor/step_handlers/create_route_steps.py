import json
import math
import pytz
from datetime import datetime
from decimal import Decimal

from src.database.chat_state import update_chat_state
from src.constructor.services.vehicle_crud import get_user_vehicles
from src.constructor.bot_response import respond_with_text, respond_with_inline_keyboard
from src.constructor.services.tg_keyboard import build_indexed_keyboard


def parse_floats_to_decimals(data: dict) -> dict:
    for key in data.keys():
        if isinstance(data[key], float):
            data[key] = round(Decimal(data[key]), 2)

    return data


create_route_sequence = [
    "routeName", "sourceLocation", "destinationLocation", "rideStartTime", "pricePerPerson", "maxPassengerCapacity"
]

step_conf = {
    "routeName": {
        "lookup_key": "text",
        "bot_response_message": "Please share the starting location! Use Telegram built-in 'share location' attachment!"
    },
    "sourceLocation": {
        "lookup_key": "location",
        "bot_response_message": "Please share the destination location! Use Telegram built-in 'share location' attachment!"
    },
    "destinationLocation": {
        "lookup_key": "location",
        "bot_response_message": "Please enter the ride start time! (dd.MM.yyyy hh:mm)"
    },
    "rideStartTime": {
        "lookup_key": "text",
        "bot_response_message": "Please enter the price per each person! (Finney)"
    },
    "pricePerPerson": {
        "lookup_key": "text",
        "bot_response_message": "Please enter the maximum passenger capacity!"
    },
    "maxPassengerCapacity": {
        "lookup_key": "text",
        "bot_response_message": "Please, select a vehicle for this route"
    },
}


def step_handler(data, chat_state):
    chat_id = chat_state['chat_id']
    prev_step_index = int(chat_state['current_step_index'])

    try:
        update_command_info = handle_prev_step_data(data, prev_step_index)
    except UserDataInvalid:
        respond_with_text("Please, adhere to the format provided!", chat_id)
        return

    old_command_info = json.loads(chat_state['command_info'])
    new_command_info = old_command_info | update_command_info
    chat_state["command_info"] = json.dumps(new_command_info)

    step_name = create_route_sequence[prev_step_index]
    if step_name == "maxPassengerCapacity":
        username = chat_state["username"]
        vehicles = get_user_vehicles(username)
        licenses = [v[0] for v in vehicles]
        if not licenses:
            respond_with_text("You do not have any vehicles registered!", chat_id)

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
                    "keyboard_name": "select_route_vehicle_keyboard",
                }
            }
        )

        chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})
        update_chat_state(chat_state)
        return

    chat_state["current_step_index"] = prev_step_index + 1
    update_chat_state(chat_state)

    respond_with_text(step_conf[step_name]["bot_response_message"], chat_id)


def handle_prev_step_data(data: dict, prev_step_index: int) -> dict:
    key = create_route_sequence[prev_step_index]
    tg_message_lookup_key = step_conf[key]["lookup_key"]
    validator_by_key = {
        "routeName": do_not_validate,
        "rideStartTime": validate_start_time,
        "sourceLocation": do_not_validate,
        "destinationLocation": do_not_validate,
        "pricePerPerson": validate_price_per_person,
        "maxPassengerCapacity": validate_max_capacity,
    }
    key_validator = validator_by_key[key]
    try:
        is_valid = key_validator(data["message"][tg_message_lookup_key])
        if not is_valid:
            raise UserDataInvalid
    except KeyError as error:
        raise UserDataInvalid

    converter_by_key = {
        "pricePerPerson": float,
        "maxPassengerCapacity": int
    }

    if formatter := converter_by_key.get(key):
        data["message"][tg_message_lookup_key] = formatter(data["message"][tg_message_lookup_key])

    update_command_info = {
        key: data["message"][tg_message_lookup_key]
    }
    return update_command_info


def validate_start_time(start_time: str) -> bool:
    """
    correct format -> dd.MM.yyyy hh:mm
    """
    date_format = "%d.%m.%Y %H:%M"
    try:
        timezone = pytz.timezone('Etc/GMT-4')
        start_time = timezone.localize(datetime.strptime(start_time, date_format))
        if start_time > datetime.now(pytz.timezone('Etc/GMT-4')):
            return True
    except ValueError:
        return False

    return False


def validate_max_capacity(max_capacity: str) -> bool:
    try:
        converted_mc = float(max_capacity)
    except Exception:
        return False
    return is_number(converted_mc) and 1 <= converted_mc < 40 and converted_mc == math.floor(converted_mc)


def is_number(value):
    return isinstance(value, (int, float))


def validate_price_per_person(price_per_person: str) -> bool:
    try:
        converted_ppp = float(price_per_person)
    except Exception:
        return False
    return is_number(converted_ppp) and converted_ppp >= 0


def do_not_validate(dummy) -> True:
    return True


class UserDataInvalid(Exception):
    ...
