# global commands
from src.constructor.command_handlers import (
    start_command, random_command, register_command, login_command, update_password_command, update_wallet_info_command,
    show_rating_command
)
# route commands
from src.constructor.command_handlers import (
    create_route_command, delete_route_command, show_routes_command, join_route_command, start_route_command
)

# vehicle commands
from src.constructor.command_handlers import (
    add_vehicle_command, show_vehicles_command, delete_vehicle_command,
)

map_command_to_handler = {
    "/start": start_command,
    "/random": random_command,
    "/register": register_command,
    "/login": login_command,
    "/updatePassword": update_password_command,
    "/updateWalletInfo": update_wallet_info_command,
    "/createRoute": create_route_command,
    "/showMyRoutes": show_routes_command,
    "/deleteRoute": delete_route_command,
    "/joinRoute": join_route_command,
    "/startRoute": start_route_command,
    "/showVehicles": show_vehicles_command,
    "/addVehicle": add_vehicle_command,
    "/deleteVehicle": delete_vehicle_command,
    "/showMyRating": show_rating_command,
}


def handle_command(data: dict, chat_state: dict):
    message = str(data["message"]["text"])
    response = 'Unknown command. Please, check the menu for available commands list.'

    split_message = message.split(' ')
    command, arguments = split_message[0], ''.join(split_message[1:])

    if command := map_command_to_handler.get(command):
        response = command.handler(data, chat_state)

    return response
