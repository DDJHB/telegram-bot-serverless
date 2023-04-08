
from src.constructor.step_handlers import (
    create_route_steps
)


def handle_step(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    if not chat_state or not chat_state['active_command']:
        return "Please, enter a command first!"

    active_command = chat_state['active_command']
    step_handler = map_active_command_to_handler(active_command)
    if not step_handler:
        return "This feature has not been developed yet..."

    return step_handler(data, chat_state)


def map_active_command_to_handler(active_command: str):
    mapped_handlers = {
        "createRoute": create_route_steps.step_handler
    }
    return mapped_handlers.get(active_command)
