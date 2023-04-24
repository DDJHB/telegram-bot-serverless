import json

from src.database.routes import get_route_by_id, update_route, put_passenger_route
from src.constructor.bot_response import respond_with_text


def handle_tx_logs(tx_logs, tx_data):
    print(tx_logs)
    additional_info = json.loads(tx_data["additional_information"])

    route = get_route_by_id(additional_info["route_id"])
    if not route:
        return
    username = additional_info["username"]
    chat_id = additional_info["chat_id"]
    if deposit_status := tx_logs[0]['args'].get('status'):
        print(deposit_status)
        if deposit_status:
            route.update({"joined_users_count": route["joined_users_count"] + 1})
            update_route(route)

            put_passenger_route(
                driver_route=route,
                username=username,
                chat_id=chat_id,
            )

            respond_with_text(f"Successfully joined route {route.get('route_name', 'random')}", chat_id)
        else:
            respond_with_text(f"There was an error with money withdrawal on your wallet", chat_id)
