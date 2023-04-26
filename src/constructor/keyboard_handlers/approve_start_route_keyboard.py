import json
import math

from src.database.routes import get_route_by_id, update_route
from src.constructor.bot_response import respond_with_text


def handler(keyboard_id, callback_query, chat_state):
    indicator, route_id = callback_query['data'].split("+")
    route = get_route_by_id(route_id)
    approval_info = json.loads(route["approval_info"])
    half_count = math.floor(route["joined_users_count"] / 2)

    if indicator == "YES":
        if approval_info["YES"] >= half_count:
            route.update({"has_started": True})
            update_route(route)
            respond_with_text("Your ride has started!", route["chat_id"])

        approval_info["YES"] = approval_info["YES"] + 1
        route.update({"approval_info": approval_info})
    else:
        if approval_info["NO"] >= half_count:
            respond_with_text("The route cannot start. Passengers have not confirmed the route start.",
                              route["chat_id"])
            approval_info = {
                "YES": 0,
                "NO": 0,
            }
        else:
            approval_info["NO"] = approval_info["NO"] + 1

        route.update({"approval_info": approval_info})

    route['approval_info'] = json.dumps(route['approval_info'])
    update_route(route)
