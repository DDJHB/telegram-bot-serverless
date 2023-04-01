
from src.constructor.command_handlers import (
    start_command, random_command, register_command, login_command, createRoute
)

map_command_to_handler = {
    "/start": start_command.handler,
    "/random": random_command.handler,
    "/register": register_command.handler,
    "/login": login_command.handler,
    "/createRoute": createRoute.handler,
}


def handle_command(data):
    message = str(data["message"]["text"])
    response = 'Unknown command. Please, check the menu for available commands list.'
    split_message = message.split(' ')
    command, arguments = split_message[0], ''.join(split_message[1:])
    if handler := map_command_to_handler.get(command):
        response = handler(data)

    return response
