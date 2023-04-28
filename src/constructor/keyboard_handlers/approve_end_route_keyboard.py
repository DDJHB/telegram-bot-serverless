import json
import math

from src.constructor.services.ranking import rate_driver
from src.database.routes import get_route_by_id, update_route, get_passengers_routes_by_route_id
from src.database.user_info import get_user_info_record
from src.constructor.payment_handlers.payment_utils import transfer
from src.constructor.bot_response import respond_with_text, delete_message


def handler(keyboard_id, callback_query, chat_state):
    indicator, route_id = callback_query['data'].split("+")
    route = get_route_by_id(route_id)
    approval_info = json.loads(route["approval_info"])
    half_count = (approval_info["start"]["YES"] + approval_info["start"]["NO"]) / 2
    chat_id = callback_query["from"]["id"]

    if indicator == "YES":
        approval_info["end"]["YES"] = approval_info["end"]["YES"] + 1

        if approval_info["end"]["YES"] >= half_count and not route.get('has_ended'):
            passenger_routes = get_passengers_routes_by_route_id(route_id)['Items']

            passenger_usernames = [item["username"] for item in passenger_routes]
            passenger_wallet_addresses = [get_user_info_record(username)["wallet_address"] for username in passenger_usernames]

            total_amount = route["pricePerPerson"] * len(passenger_routes)
            print(passenger_wallet_addresses, total_amount)
            transfer(passenger_wallet_addresses, route["owner_username"], total_amount, route["owner_chat_id"])

            for passenger_route in passenger_routes:
                respond_with_text("Your ride has ended!", passenger_route["chat_id"])
                rate_driver(passenger_route)

            respond_with_text("Your ride has ended!", route["chat_id"])
            route.update({
                "has_ended": True
            })

        route.update({"approval_info": approval_info})
    else:
        approval_info["end"]["NO"] = approval_info["end"]["NO"] + 1

        if approval_info["end"]["NO"] > half_count:
            respond_with_text("Cannot end the route. Passengers have to confirm the end of the route.",
                              route["chat_id"])
            approval_info["end"] = {
                "YES": 0,
                "NO": 0,
            }

        route.update({"approval_info": approval_info})

    route['approval_info'] = json.dumps(route['approval_info'])
    update_route(route)

    delete_message(chat_id, keyboard_id)
