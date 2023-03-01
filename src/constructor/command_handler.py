
from src.constructor.command_handlers import start_command, random_command

map_command_to_handler = {
    "/start": start_command.handler,
    "/random": random_command.handler,
}


def handle_command(data):
    message = str(data["message"]["text"])
    response = 'Unknown command. Please, check the menu for available commands list.'
    if handler := map_command_to_handler.get(message):
        response = handler(data)

    return response
