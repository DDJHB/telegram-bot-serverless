
from src.constructor.command_handlers.other_commands import (
    help_command, start_command, random_command, show_rating_command
)

from src.constructor.command_handlers.account_management_commands import (
    update_password_command, delete_account_command, update_wallet_info_command, login_command, register_command
)

from src.constructor.command_handlers.route_commands import (
    delete_route_command, create_route_command, show_routes_command,
    start_route_command, end_route_command, join_route_command,
    show_joined_routes_command, leave_route,
)

from src.constructor.command_handlers.vehicle_commands import (
    show_vehicles_command, delete_vehicle_command, add_vehicle_command
)

map_command_to_handler = {
    "/start": start_command,
    "/random": random_command,
    "/register": register_command,
    "/login": login_command,
    "/update_password": update_password_command,
    "/update_wallet_info": update_wallet_info_command,
    "/delete_account": delete_account_command,
    "/create_route": create_route_command,
    "/show_my_routes": show_routes_command,
    "/delete_route": delete_route_command,
    "/join_route": join_route_command,
    "/start_route": start_route_command,
    "/end_route": end_route_command,
    "/show_vehicles": show_vehicles_command,
    "/add_vehicle": add_vehicle_command,
    "/delete_vehicle": delete_vehicle_command,
    "/show_my_rating": show_rating_command,
    "/show_joined_routes": show_joined_routes_command,
    "/leave_route": leave_route,
    "/help": help_command,
}


def handle_command(data: dict, chat_state: dict):
    message = str(data["message"]["text"])
    response = 'Unknown command. Please, check the menu for available commands list.'

    split_message = message.split(' ')
    command, arguments = split_message[0], ''.join(split_message[1:])

    if command := map_command_to_handler.get(command):
        response = command.handler(data, chat_state)

    return response
