import random


def handle_command(message, data):
    first_name = data["message"]["chat"]["first_name"]
    response = 'Unknown command. Please, check the menu for available commands list.'
    if "/start" == message:
        response = f"Hello {first_name}"
    if "/random" == message:
        response = str(random.randint(0, 100))

    return response
