
# global commands
from src.constructor.command_handlers import (
    start_command, random_command, register_command, login_command
)
# route commands
from src.constructor.command_handlers import (
    create_route_command, delete_route_command, show_routes_command
)

map_command_to_handler = {
    "/start": start_command.handler,
    "/random": random_command.handler,
    "/register": register_command.handler,
    "/login": login_command.handler,
    "/createRoute": create_route_command.handler,
    "/showMyRoutes": show_routes_command.handler,
    #"/deleteRoute": delete_route_command.handler,
}


def handle_command(data: dict, chat_state: dict):
    message = str(data["message"]["text"])
    response = 'Unknown command. Please, check the menu for available commands list.'
    split_message = message.split(' ')
    command, arguments = split_message[0], ''.join(split_message[1:])
    if handler := map_command_to_handler.get(command, chat_state):
        response = handler(data)

    return response
