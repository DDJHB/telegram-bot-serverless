# global commands
from src.constructor.command_handlers import (
    start_command, random_command, register_command, login_command, add_wallet_command
)
# route commands
from src.constructor.command_handlers import (
    create_route_command, delete_route_command, show_routes_command, search_routes_command
)

map_command_to_handler = {
    "/start": start_command,
    "/random": random_command,
    "/register": register_command,
    "/login": login_command,
    "/createRoute": create_route_command,
    "/addWallet": add_wallet_command,
    "/showMyRoutes": show_routes_command,
    "/deleteRoute": delete_route_command,
    "/searchRoutes": search_routes_command,
}


def handle_command(data: dict, chat_state: dict):
    message = str(data["message"]["text"])
    response = 'Unknown command. Please, check the menu for available commands list.'

    split_message = message.split(' ')
    command, arguments = split_message[0], ''.join(split_message[1:])

    if command := map_command_to_handler.get(command):
        response = command.handler(data, chat_state)

    return response
