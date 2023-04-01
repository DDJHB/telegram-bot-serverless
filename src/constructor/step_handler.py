import json


from src.database.chat_state import get_chat_state_record
from src.constructor.step_handlers import (
    create_route_steps
)


def handle_step(data):
    chat_id = data["message"]["chat"]["id"]
    record = get_chat_state_record(chat_id)
    if not record or not record['state']:
        return "Wait for the launch of the bot..."

    state = json.loads(record['state'])
    step_handler = map_active_command_to_handler(state['activeCommand'])
    return step_handler(data, record)


def map_active_command_to_handler(active_command):
    mapped_handlers = {
        "createRoute": create_route_steps.step_handler
    }
    return mapped_handlers.get(active_command)
