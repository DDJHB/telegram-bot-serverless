
from src.database.chat_state import get_chat_state
from src.constructor.step_handlers import (
    create_route_steps,
    register_steps,
    update_password_steps,
    update_wallet_info_steps,
    add_vehicle_steps,
    delete_route_steps,
    join_route_steps, delete_account_steps,
)
from src.constructor.bot_response import respond_with_text


def handle_step(data: dict, chat_state: dict):
    chat_id = chat_state["chat_id"]
    if not chat_state or not chat_state.get('active_command'):
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
        "joinRoute": join_route_steps,
        "deleteRoute": delete_route_steps,
        "createRoute": create_route_steps,
        "register": register_steps,
        "updatePassword": update_password_steps,
        "updateWalletInfo": update_wallet_info_steps,
        "deleteAccount": delete_account_steps,
        "addVehicle": add_vehicle_steps,
    }
    return mapped_handlers.get(active_command)
