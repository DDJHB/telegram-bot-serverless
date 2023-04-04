import json
import math
from datetime import datetime
from decimal import Decimal

from src.database.chat_state import update_chat_state
from src.database.routes import put_route


def parse_floats_to_decimals(data: dict) -> dict:
    for key in data.keys():
        if isinstance(data[key], float):
            data[key] = round(Decimal(data[key]), 2)

    return data


create_route_sequence = [
    "sourceLocation", "destinationLocation", "rideStartTime", "pricePerPerson", "maxPassengerCapacity"
]

step_conf = {
    "sourceLocation": {
        "lookup_key": "location",
        "bot_response_message": "Please share the destination location! Use Telegram built-in 'share location' attachment."
    },
    "destinationLocation": {
        "lookup_key": "location",
        "bot_response_message": "Please enter the ride start time! (dd.MM.yyyy hh:mm)"
    },
    "rideStartTime": {
        "lookup_key": "text",
        "bot_response_message": "Please enter the price per each person! (USD)"
    },
    "pricePerPerson": {
        "lookup_key": "text",
        "bot_response_message": "Please enter the maximum passenger capacity!"
    },
    "maxPassengerCapacity": {
        "lookup_key": "text",
        "bot_response_message": "Route has successfully been created!"
    },
}


def step_handler(data, state_record):
    prev_step_index = int(state_record['current_step_index'])

    try:
        update_command_info = handle_prev_step_data(data, prev_step_index)
    except UserDataInvalid as error:
        return "Please, adhere to the format provided!"

    old_command_info = json.loads(state_record['command_info'])
    new_command_info = old_command_info | update_command_info
    state_record["command_info"] = json.dumps(new_command_info)

    if prev_step_index == len(create_route_sequence) - 1:
        state_record["active_command"] = None
        put_route(
            username=data["message"]["from"]["username"],
            chat_id=data["message"]["chat"]["id"],
            route_info=parse_floats_to_decimals(new_command_info),
        )
        update_chat_state(state_record)
        step_name = create_route_sequence[prev_step_index]
        return step_conf[step_name]["bot_response_message"]

    state_record["current_step_index"] = prev_step_index + 1
    update_chat_state(state_record)

    step_name = create_route_sequence[prev_step_index]
    return step_conf[step_name]["bot_response_message"]


def handle_prev_step_data(data: dict, prev_step_index: int) -> dict:
    key = create_route_sequence[prev_step_index]
    tg_message_lookup_key = step_conf[key]["lookup_key"]
    validator_by_key = {
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

    if converter := converter_by_key.get(key):
        data["message"][tg_message_lookup_key] = converter(data["message"][tg_message_lookup_key])

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
        start_time = datetime.strptime(start_time, date_format)
        if start_time > datetime.now(): # TODO FIX THE TIMEZONES - LAMBDA IS NOT AROUND
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