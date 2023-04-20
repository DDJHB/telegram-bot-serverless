
from src.constructor.step_handlers import (
    create_route_steps,
    register_steps,
    add_wallet_steps,
    update_password_steps,
    delete_route_steps,
    search_routes_steps,
)
from src.constructor.bot_response import respond_with_text


def handle_step(data: dict, chat_state: dict):
    chat_id = chat_state["chat_id"]
    if not chat_state or not chat_state['active_command']:
        respond_with_text("Please, enter a command first!", chat_id)
        return

    active_command = chat_state['active_command']
    command = map_active_command_to_handler(active_command)
    if not command:
        respond_with_text("Please, enter a command first!", chat_id)
        return

    return command.step_handler(data, chat_state)


def map_active_command_to_handler(active_command: str):
    mapped_handlers = {
        "searchRoutes": search_routes_steps,
        "deleteRoute": delete_route_steps,
        "createRoute": create_route_steps,
        "register": register_steps,
        "addWallet": add_wallet_steps,
        "updatePassword": update_password_steps,
    }
    return mapped_handlers.get(active_command)
