import json
from src.database.chat_state import update_chat_state
from src.database.routes import get_user_routes
from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data["message"]["chat"]["username"]

    owned_routes = get_user_routes(username)
    if owned_routes.get("Items", []):
        respond_with_text("Please, delete all created routes in order to proceed!", chat_id)
        return

    joined_routes = get_user_routes(username=username, is_passenger=True)
    if joined_routes.get("Items", []):
        respond_with_text("Please, leave all joined routes to proceed!", chat_id)
        return

    command_state = {
        "active_command": "deleteAccount",
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }

    chat_state.update(command_state)
    update_chat_state(chat_state)

    return "To delete your account, please enter current password!"
