import json
import re
import datetime

from src.constructor.services.vehicle_crud import add_user_vehicle
from src.database.chat_state import update_chat_state

vehicle_register_sequence = [
    "license", "model", "color", "year"
]

step_conf = {
    "license": {
        "bot_response_message": "Please enter your vehicle model!"
    },
    "model": {
        "bot_response_message": "Please enter your vehicle color!"
    },
    "color": {
        "bot_response_message": "Please enter your vehicle year!"
    },
    "year": {
        "bot_response_message": "Registering vehicle..."
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

    if prev_step_index == len(vehicle_register_sequence) - 1:
        add_user_vehicle(
            username=data["message"]["chat"]["username"],
            vehicle=new_command_info,
            chat_id=data["message"]["chat"]["id"],
        )

        state_record["active_command"] = None

    state_record["current_step_index"] = prev_step_index + 1
    update_chat_state(state_record)

    step_name = vehicle_register_sequence[prev_step_index]
    return step_conf[step_name]["bot_response_message"]


def handle_prev_step_data(data: dict, prev_step_index: int) -> dict:
    key = vehicle_register_sequence[prev_step_index]
    validator_by_key = {
        "license": validate_license,
        "model": do_not_validate,
        "color": do_not_validate,
        "year": validate_year,
    }
    key_validator = validator_by_key[key]
    try:
        is_valid = key_validator(data["message"]['text'])
        if not is_valid:
            raise UserDataInvalid
    except KeyError as error:
        raise UserDataInvalid

    update_command_info = {
        key: data["message"]['text']
    }
    return update_command_info


def do_not_validate(dummy) -> True:
    return True


def validate_year(year: int):
    current_year = datetime.datetime.now().year
    if 1950 <= year <= current_year:
        return True
    else:
        return False


def validate_license(license_number: str):
    pattern = r"^(?!00)\d{2}[A-Za-z]{2}(?!000)\d{3}$"
    if re.match(pattern, license_number):
        return True
    else:
        return False


class UserDataInvalid(Exception):
    ...

