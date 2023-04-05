from src.database.chat_state import get_chat_state
from src.constructor.step_handlers import (
    create_route_steps,
    register_steps,
    add_wallet_steps,
)


def handle_step(data):
    chat_id = data["message"]["chat"]["id"]
    record = get_chat_state(chat_id)
    if not record or not record['active_command']:
        return "Please, enter a command first!"

    active_command = record['active_command']
    step_handler = map_active_command_to_handler(active_command)
    if not step_handler:
        return "This feature has not been developed yet..."

    return step_handler(data, record)


def map_active_command_to_handler(active_command: str):
    mapped_handlers = {
        "createRoute": create_route_steps.step_handler,
        "register": register_steps.step_handler,
        "addWallet": add_wallet_steps.step_handler,
    }
    return mapped_handlers.get(active_command)
