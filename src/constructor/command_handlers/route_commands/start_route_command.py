import json

from src.constructor.bot_response import respond_with_text, respond_with_inline_keyboard
from src.constructor.services.tg_keyboard import build_view_keyboard, extend_keyboard_with_route_id_buttons
from src.database.chat_state import update_chat_state
from src.database.routes import get_user_routes


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']

    respond_with_text("Select route number below", chat_id)

    response = get_user_routes(username)
    routes = response['Items']
    keyboard_def = extend_keyboard_with_route_id_buttons(build_view_keyboard(routes), routes)
    tg_response = respond_with_inline_keyboard(
        parent_message="Your routes:",
        keyboard_definition=keyboard_def,
        chat_id=chat_id,
    )

    keyboard_id = str(tg_response.json()['result']["message_id"])
    current_page = 1
    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    global_keyboards_info.update(
        {
            keyboard_id: {
                "keyboard_name": "start_route_keyboard",
                "page_info": {
                    "last_evaluated_keys": {str(current_page): response.get('LastEvaluatedKey')},
                    "current_page_number": current_page,
                },
            }
        }
    )

    chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})

    command_state = {
        "active_command": "startRoute",
        "current_step_index": 0,
        "command_info": json.dumps({}),
    }
    chat_state.update(command_state)

    update_chat_state(chat_state)