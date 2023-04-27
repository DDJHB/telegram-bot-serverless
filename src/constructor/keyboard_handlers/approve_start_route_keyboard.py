import json
import math

from src.database.routes import get_route_by_id, update_route
from src.constructor.bot_response import respond_with_text, delete_message


def handler(keyboard_id, callback_query, chat_state):
    indicator, route_id = callback_query['data'].split("+")
    route = get_route_by_id(route_id)
    approval_info = json.loads(route["approval_info"])
    half_count = math.floor(route["joined_users_count"] / 2)
    chat_id = callback_query["from"]["id"]

    if indicator == "YES":
        approval_info["start"]["YES"] = approval_info["start"]["YES"] + 1

        if approval_info["start"]["YES"] >= half_count:
            route.update({"has_started": True})
            update_route(route)
            respond_with_text("Your ride has started!", route["chat_id"])

        route.update({"approval_info": approval_info})
    else:
        approval_info["start"]["NO"] = approval_info["start"]["NO"] + 1

        if approval_info["start"]["NO"] >= half_count:
            respond_with_text("The route cannot start. Passengers have not confirmed the route start.",
                              route["chat_id"])
            approval_info = {
                "start": {
                    "YES": 0,
                    "NO": 0,
                },
                "end": {
                    "YES": 0,
                    "NO": 0,
                }
            }

        route.update({"approval_info": approval_info})

    route['approval_info'] = json.dumps(route['approval_info'])
    update_route(route)

    delete_message(chat_id, keyboard_id)