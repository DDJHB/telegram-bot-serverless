import json

from src.database.routes import get_route_by_id, update_route, delete_passenger_route
from src.constructor.bot_response import respond_with_text, delete_message


def handle_tx_logs(tx_logs, tx_data):
    print(tx_logs)
    additional_info = json.loads(tx_data["additional_information"])

    route = get_route_by_id(additional_info["route_id"])
    if not route:
        return
    username = additional_info["username"]
    chat_id = additional_info["chat_id"]
    if withdraw_status := tx_logs[0]['args'].get('status'):
        print(withdraw_status)
        if withdraw_status:
            route.update({"joined_users_count": route["joined_users_count"] - 1})
            update_route(route)

            delete_passenger_route(
                username=username,
                route_id=route["route_id"],
            )

            delete_message(chat_id, additional_info["keyboard_id"])
            respond_with_text(f"Successfully left route {route.get('route_name', 'random')}", chat_id)
        else:
            respond_with_text(f"There was an error with cost refund to your wallet", chat_id)
