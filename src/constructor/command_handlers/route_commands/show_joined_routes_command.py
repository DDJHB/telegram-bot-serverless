import json

from src.database.chat_state import update_chat_state
from src.database.routes import get_user_routes
from src.constructor.bot_response import respond_with_inline_keyboard, respond_with_text
from src.constructor.services.tg_keyboard import build_view_keyboard

KEYBOARD_NAME = "joined_routes_keyboard"


def handler(data: dict, chat_state: dict):
    chat_id = data["message"]["chat"]["id"]
    username = data['message']['from']['username']

    response = get_user_routes(username=username, is_passenger=True)
    if not response.get("Items", []):
        respond_with_text("You have not joined any routes yet!", chat_id)
        return

    keyboard_definition = build_view_keyboard(response['Items'])
    tg_response = respond_with_inline_keyboard(
        parent_message="Joined Routes:",
        keyboard_definition=keyboard_definition,
        chat_id=chat_id,
    )

    keyboard_id = str(tg_response.json()['result']["message_id"])
    current_page = 1
    global_keyboards_info = json.loads(chat_state.get("global_keyboards_info") or '{}')
    global_keyboards_info.update(
        {
            keyboard_id: {
                "keyboard_name": KEYBOARD_NAME,
                "page_info": {
                    "last_evaluated_keys": {str(current_page): response.get('LastEvaluatedKey')},
                    "current_page_number": current_page,
                },
            }
        }
    )

    chat_state.update({"global_keyboards_info": json.dumps(global_keyboards_info)})

    update_chat_state(chat_state)
