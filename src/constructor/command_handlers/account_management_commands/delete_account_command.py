import json
from src.database.chat_state import put_chat_state
from src.database.routes import get_user_routes
from src.constructor.bot_response import respond_with_text


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data["message"]["chat"]["id"]

    owned_routes = get_user_routes(username)

    if not owned_routes.get("Items"):
        respond_with_text("Please, delete all created routes in order to proceed!", chat_id)
        return

    # TODO check joined routes of user

    command_state = {
        "active_command": "deleteAccount",
        "current_step_index": 0,
        "command_info": json.dumps({}),
        "login_timestamp": chat_state['login_timestamp'],
    }

    put_chat_state(chat_id, command_state)

    return "To delete your account, please enter current password!"
