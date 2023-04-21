import json

from src.database.chat_state import update_chat_state
from src.constructor.services.vehicle_crud import get_user_vehicles
from src.constructor.bot_response import respond_with_inline_keyboard
from src.constructor.services.tg_keyboard import build_view_keyboard

keyboard_name = "routes_keyboard"


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']

    response = get_user_vehicles(username)
    keyboard_definition = build_view_keyboard(response)
    tg_response = respond_with_inline_keyboard(
        parent_message="Your vehicles:",
        keyboard_definition=keyboard_definition,
        chat_id=chat_id,
    )
    keyboard_id = str(tg_response.json()['result']["message_id"])
    current_page = 1
    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    global_keyboards_info.update(
        {
            keyboard_id: {
                "keyboard_name": "routes_keyboard",
                "page_info": {
                    "last_evaluated_keys": {str(current_page): response.get('LastEvaluatedKey')},
                    "current_page_number": current_page,
                },
            }
        }
    )

    chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})

    update_chat_state(chat_state)
