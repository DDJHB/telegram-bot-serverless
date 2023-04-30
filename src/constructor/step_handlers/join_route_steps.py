import json
from datetime import datetime
import pytz

from src.constructor.bot_response import respond_with_text, respond_with_inline_keyboard
from src.database.chat_state import update_chat_state
from src.constructor.services.route import compute_routes
from src.constructor.services.tg_keyboard import build_view_keyboard, extend_keyboard_with_route_id_buttons


# TODO: validate and not return the routes that have reached max capacity

join_routes_sequence = [
    "sourceLocation", "destinationLocation", "searchProximity", "rideStartTimeRange",
]

step_conf = {
    "sourceLocation": {
        "lookup_key": "location",
        "bot_response_message": "Please share the destination location! "
                                "Use Telegram built-in 'share location' attachment!"
    },
    "destinationLocation": {
        "lookup_key": "location",
        "bot_response_message": "What proximity range suits you? Please, enter one of the following - Long, Mid, Close"
    },
    "searchProximity": {
        "lookup_key": "text",
        "bot_response_message": "Please enter the ride start time range! (dd.MM.yyyy hh:mm - dd.MM.yyyy hh:mm)"
    },
    "rideStartTimeRange": {
        "lookup_key": "text",
        "bot_response_message": None
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

    step_name = join_routes_sequence[prev_step_index]

    if prev_step_index == len(join_routes_sequence) - 1:
        chat_state["active_command"] = None
        routes_info = compute_routes(new_command_info)
        routes = routes_info.get("Items", [])
        if not routes:
            respond_with_text("No suitable routes found!", chat_id)
            return
        keyboard_definition = extend_keyboard_with_route_id_buttons(build_view_keyboard(routes), routes)
        tg_response = respond_with_inline_keyboard(
            parent_message="Found Routes:",
            keyboard_definition=keyboard_definition,
            chat_id=chat_id,
        )
        keyboard_id = str(tg_response.json()['result']["message_id"])
        current_page = 1
        global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
        global_keyboards_info.update(
            {
                keyboard_id: {
                    "keyboard_name": "join_route_keyboard",
                    "page_info": {
                        "last_evaluated_keys": {str(current_page): routes_info.get('LastEvaluatedKey')},
                        "current_page_number": current_page,
                    },
                    "search_info": new_command_info,
                }
            }
        )

        chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})

        update_chat_state(chat_state)
        if response_message := step_conf[step_name]["bot_response_message"]:
            respond_with_text(response_message, chat_id)
        return

    chat_state["current_step_index"] = prev_step_index + 1
    update_chat_state(chat_state)

    respond_with_text(step_conf[step_name]["bot_response_message"], chat_id)


def handle_prev_step_data(data: dict, prev_step_index: int) -> dict:
    key = join_routes_sequence[prev_step_index]
    tg_message_lookup_key = step_conf[key]["lookup_key"]
    validator_by_key = {
        "rideStartTimeRange": validate_start_time_range,
        "sourceLocation": do_not_validate,
        "destinationLocation": do_not_validate,
        "searchProximity": validate_search_proximity,
    }

    key_validator = validator_by_key[key]
    try:
        is_valid = key_validator(data["message"][tg_message_lookup_key])
        if not is_valid:
            raise UserDataInvalid
    except KeyError as error:
        raise UserDataInvalid

    formatter_by_key = {
        "searchProximity": lower_string_case,
    }

    if formatter := formatter_by_key.get(key):
        data["message"][tg_message_lookup_key] = formatter(data["message"][tg_message_lookup_key])

    update_command_info = {
        key: data["message"][tg_message_lookup_key]
    }
    return update_command_info


def lower_string_case(string: str) -> str:
    return string.lower()


def do_not_validate(dummy) -> True:
    return True


def validate_search_proximity(proximity: str) -> bool:
    allowed_values = ["long", "mid", "close"]
    if proximity.lower() in allowed_values:
        return True
    return False


def validate_start_time_range(time_range: str) -> bool:
    """
    correct format for single date -> dd.MM.yyyy hh:mm
    format for range -> dd.MM.yyyy hh:mm - dd.MM.yyyy hh:mm
    """
    if "-" not in time_range:
        return False

    if time_range.count("-") > 2:
        return False

    lb_time, ub_time = map(lambda x: x.strip(), time_range.split("-"))

    date_format = "%d.%m.%Y %H:%M"
    try:
        compare_time_order(lb_time, ub_time)
        for start_time in (lb_time, ub_time):
            timezone = pytz.timezone('Etc/GMT-4')
            start_time = timezone.localize(datetime.strptime(start_time, date_format))
            if start_time < datetime.now(pytz.timezone('Etc/GMT-4')):
                return False
    except ValueError:
        return False

    return True


def compare_time_order(time_a, time_b):
    date_format = "%d.%m.%Y %H:%M"
    timezone = pytz.timezone('Etc/GMT-4')
    t_time_a = timezone.localize(datetime.strptime(time_a, date_format))
    t_time_b = timezone.localize(datetime.strptime(time_b, date_format))
    return t_time_a < t_time_b


class UserDataInvalid(Exception):
    ...
