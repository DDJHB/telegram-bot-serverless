import json
from decimal import Decimal

from src.database.chat_state import update_chat_state
from src.database.routes import delete_user_route, get_route_by_name
from src.constructor.bot_response import respond_with_text


def parse_floats_to_decimals(data: dict) -> dict:
    for key in data.keys():
        if isinstance(data[key], float):
            data[key] = round(Decimal(data[key]), 2)

    return data


delete_route_sequence = [
    "routeName"
]

step_conf = {
    "routeName": {
        "lookup_key": "text",
        "bot_response_message": "Route has been deleted successfully!"
    },
}


def step_handler(data, chat_state):
    chat_id = chat_state['chat_id']
    prev_step_index = int(chat_state['current_step_index'])

    try:
        update_command_info = handle_prev_step_data(data, prev_step_index)
    except UserDataInvalid as error:
        respond_with_text(str(error), chat_id)
        return

    old_command_info = json.loads(chat_state['command_info'])
    new_command_info = old_command_info | update_command_info
    chat_state["command_info"] = json.dumps(new_command_info)

    if prev_step_index == len(delete_route_sequence) - 1:
        username = data["message"]["from"]["username"]
        chat_state["active_command"] = None
        user_route = get_route_by_name(username=username, route_name=new_command_info["routeName"])
        delete_user_route(user_route["pk"], user_route["sk"])
        update_chat_state(chat_state)
        step_name = delete_route_sequence[prev_step_index]
        respond_with_text(step_conf[step_name]["bot_response_message"], chat_id)
        return

    chat_state["current_step_index"] = prev_step_index + 1
    update_chat_state(chat_state)

    step_name = delete_route_sequence[prev_step_index]
    respond_with_text(step_conf[step_name]["bot_response_message"], chat_id)


def handle_prev_step_data(data: dict, prev_step_index: int) -> dict:
    key = delete_route_sequence[prev_step_index]
    tg_message_lookup_key = step_conf[key]["lookup_key"]
    validator_by_key = {
        "routeName": check_route_exists,
    }
    key_validator = validator_by_key[key]
    try:
        username = data['message']["from"]["username"]
        route_name = data["message"][tg_message_lookup_key]
        is_valid, message = key_validator(username, route_name)
        if not is_valid:
            raise UserDataInvalid(message)
    except KeyError:
        raise UserDataInvalid("Please, adhere to the format provided!")

    update_command_info = {
        key: data["message"][tg_message_lookup_key]
    }

    return update_command_info


def check_route_exists(username: str, route_name: str):
    user_route = get_route_by_name(username=username, route_name=route_name)
    if not user_route:
        return False, f"Route with name '{route_name}' does not exist!"

    return True, ""


class UserDataInvalid(Exception):
    ...
