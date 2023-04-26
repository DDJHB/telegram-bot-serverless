import json
from decimal import Decimal

from src.database.routes import put_route
from src.database.chat_state import update_chat_state
from src.constructor.bot_response import respond_with_text


def handler(keyboard_id, callback_query, chat_state):
    vehicle_index = callback_query['data']

    username = callback_query["from"]["username"]
    chat_id = callback_query["from"]["id"]

    chat_state["active_command"] = None
    command_info = json.loads(chat_state["command_info"])
    command_info.update({"vehicle_index": vehicle_index})
    chat_state["command_info"] = json.dumps(command_info)
    update_chat_state(chat_state)

    put_route(
        username=username,
        chat_id=chat_id,
        route_name=command_info["routeName"],
        route_info=parse_floats_to_decimals(command_info),
    )

    respond_with_text("Route has been successfully created!", chat_id)


def parse_floats_to_decimals(data: dict) -> dict:
    for key in data.keys():
        if isinstance(data[key], float):
            data[key] = round(Decimal(data[key]), 2)

    return data